# below is point_charges.py

# necessary imports

import pygame 
import numpy as np
from constants_for_all_files import *

# Point Charge Class

class PointCharge:

    def __init__(self, pos_0, charge, mass, environmental, static, pc_id):
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

        # Initialize radius values (will be updated by update_relative_scale)
        self.core_radius = 15  # default core radius
        self.border_radius = 6  # default border radius
        self.total_radius = self.core_radius + self.border_radius

        self.color = (200, 0, 0) if charge > 0 else (0, 0, 200) # Red for Positive, Blue for Negative

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

        # reverts to initial state
        
        if not self.environmental:
            self.pos = self.pos_0.copy()
            self.vel = self.vel_0.copy()
        else:
            # delete the point charge if NOT environmental
            del self
    
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