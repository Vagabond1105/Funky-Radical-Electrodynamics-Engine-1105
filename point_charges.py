# below is point_charges.py

# necessary imports

import pygame 
import numpy as np
from constants_for_all_files import *
from collections import deque

# Point Charge Class

class PointCharge:

    def __init__(self, pos_0, charge, mass, environmental, static, pc_id,e):
        self.position = np.array(pos_0, dtype=float) # Position Vector
        self.vel = np.array([0.0, 0.0], dtype=float) # Velocity Vector
        self.pos_0 = np.array(pos_0, dtype=float) # Initial Position Vector
        self.vel_0 = np.array([0.0, 0.0], dtype=float) # Initial Velocity Vector
        self.charge = charge # Charge in Coulombs
        self.mass = mass # Mass in kg
        self.environmental = environmental # Boolean for Environmental Charge
        self.static = static # Boolean for Static Charge
        self.pc_id = pc_id # Unique ID for Point Charge
        self.dragging = False # Boolean for Dragging State
        # coefficient of restitution
        self.e = e

        # Initialize radius values (will be updated by update_relative_scale)
        self.core_radius = 15  # default core radius
        self.border_radius = 6  # default border radius
        self.total_radius = self.core_radius + self.border_radius

        self.color = (200, 0, 0) if charge > 0 else (0, 0, 200) # Red for Positive, Blue for Negative

        self.history = deque(maxlen=TRAIL_LENGTH)
        self.frame_counter = 0
        # Pre-calculate the "Ghost" surface for motion blur
        # We make a surface big enough to hold the particle
        # This is an optimization so we don't create surfaces every frame
        self.ghost_surf = pygame.Surface((self.total_radius*2, self.total_radius*2), pygame.SRCALPHA)
        # Draw the ghost shape ONCE onto this surface
        # (It's just the colored core, semi-transparent)
        pygame.draw.circle(self.ghost_surf, self.color, (self.total_radius, self.total_radius), int(self.core_radius))

    @property
    def pos(self):
        """Property to always return current position (for compatibility with electric_field.py)."""
        return self.position

    def update_relative_scale(self, all_charges):
        
        # Determines core_radius based on charge magnitude vs others.
        # Determines border_radius based on mass vs others.
        
        if not all_charges:
            return

        # 1. Calculate Core Radius (Charge)
        max_q = max(abs(pc.charge) for pc in all_charges)
        min_q = min(abs(pc.charge) for pc in all_charges)
        q_range = max_q - min_q
        
        current_q = abs(self.charge)
        
        if q_range == 0:
            norm_q = 0.5
        else:
            # (current - min) / range -> 0 to 1
            norm_q = (current_q - min_q) / q_range
            
        self.core_radius = 5 + (norm_q * 15) # Scale 5px to 20px

        # 2. Calculate Border Radius (Mass)
        max_m = max(pc.mass for pc in all_charges)
        min_m = min(pc.mass for pc in all_charges)
        m_range = max_m - min_m
        
        current_m = self.mass
        
        if m_range == 0:
            norm_m = 0.5
        else:
            norm_m = (current_m - min_m) / m_range
            
        self.border_radius = 1 + (norm_m * 4) # Scale 1px to 5px
        
        # 3. Sum for total hitbox
        self.total_radius = self.core_radius + self.border_radius

    def reset(self):
        # Always revert to initial state (position and velocity)
        self.position = self.pos_0.copy()
        self.vel = self.vel_0.copy()
        # also reset trail history when resetting particle
        try:
            self.history.clear()
            self.frame_counter = 0
        except Exception:
            pass
    
    def render(self, screen):
        # Draw Border (Mass representation) - Colored based on charge
        if self.charge > 0:
            border_colour_fill = (220, 90, 90)  # Orange for Positive Charge Border
        elif self.charge < 0:
            border_colour_fill = (130, 20, 130)  # Purple for Negative Charge Border
        else:
            border_colour_fill = (100, 100, 100)  # Grey for neutral
            
        pygame.draw.circle(screen, border_colour_fill, self.position.astype(int), int(self.total_radius))
        
        # Draw Core (Charge representation) - Colored
        pygame.draw.circle(screen, self.color, self.position.astype(int), int(self.core_radius))
        
        # Selection Highlight
        if self.dragging:
            pygame.draw.circle(screen, (255, 255, 255), self.position.astype(int), int(self.total_radius + 2), 2)
            # sets new position while dragging
            self.position = np.array(pygame.mouse.get_pos(), dtype=float)

    def record_trail(self, enabled=False):
        """Record current position into history when enabled.
        Records every TRAIL_SKIP frames. Clears history immediately when disabled.
        """
        if enabled:
            self.frame_counter += 1
            if self.frame_counter % TRAIL_SKIP == 0:
                # store a copy to avoid mutation
                self.history.append(self.position.copy())
        else:
            # Clear history immediately when disabled
            if self.history:
                self.history.clear()
            self.frame_counter = 0

    def render_trails(self, screen):
        """Render the stored trail positions with a simple fade effect.
        Older positions are more transparent. Uses small temporary surfaces with per-surface alpha.
        """
        if not self.history:
            return

        length = len(self.history)
        # Draw from oldest to newest so newer points appear on top
        for i, pos in enumerate(self.history):
            if length > 1:
                t = i / (length - 1)
            else:
                t = 1.0
            # Alpha from 40 (oldest) -> 230 (newest)
            alpha = int(40 + (230 - 40) * t)

            # Draw a small filled circle using a temporary surface to allow alpha
            r = max(1, int(self.core_radius))
            surf_size = r * 2 + 4
            surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            col = (self.color[0], self.color[1], self.color[2], alpha)
            pygame.draw.circle(surf, col, (surf_size // 2, surf_size // 2), r)
            blit_pos = (int(pos[0] - surf_size // 2), int(pos[1] - surf_size // 2))
            screen.blit(surf, blit_pos)

        

    def resolve_collision(self, other):
        """
        Resolves elastic collision with another PointCharge.
        Handles position correction (un-sticking) and velocity impulse.
        """
        # 1. Get distance vector and magnitude
        diff = self.position - other.position
        dist_sq = np.dot(diff, diff)
        min_dist = self.total_radius + other.total_radius
        
        # Optimization: Check squared distance first to avoid sqrt() if not needed
        if dist_sq >= min_dist * min_dist:
            return

        # --- COLLISION DETECTED! ---
        dist = np.sqrt(dist_sq)

        # 2. Position Correction (Prevent Sticking/Ghosting)
        # If distance is 0 (exact overlap), pick random direction to avoid divide-by-zero
        if dist == 0:
            n = np.array([1.0, 0.0])
            overlap = min_dist
        else:
            n = diff / dist # Normal vector (Direction of collision)
            overlap = min_dist - dist
        
        # Move particles apart so they just touch
        # If one is static, the other moves the full distance
        if not self.static and not other.static:
            self.position += n * (overlap / 2.0)
            other.position -= n * (overlap / 2.0)
        elif not self.static and other.static:
            self.position += n * overlap
        elif self.static and not other.static:
            other.position -= n * overlap
        else:
            return # Both static, nothing happens

        # 3. Velocity Response (1D Elastic Collision along the Normal)
        # Relative velocity
        v_rel = self.vel - other.vel
        
        # Velocity along the normal
        vel_along_normal = np.dot(v_rel, n)

        # Do not resolve if velocities are separating (they are already moving away)
        if vel_along_normal > 0:
            return

        # Elasticity (1.0 = Perfectly Elastic, 0.0 = Sticky)
        # Use an effective restitution combining both bodies (choose the smaller)
        try:
            e = min(float(self.e), float(other.e))
        except Exception:
            e = 1.0

        # Calculate Impulse Scalar (J)
        # J = -(1 + e) * (v_rel . n) / (1/m1 + 1/m2)
        inv_mass1 = 0 if self.static else 1.0 / self.mass
        inv_mass2 = 0 if other.static else 1.0 / other.mass
        
        # Infinite mass check
        if inv_mass1 + inv_mass2 == 0:
            return

        j = -(1 + e) * vel_along_normal
        j /= (inv_mass1 + inv_mass2)

        # Apply Impulse Vector
        impulse = j * n
        
        if not self.static:
            self.vel += impulse * inv_mass1
        if not other.static:
            other.vel -= impulse * inv_mass2
