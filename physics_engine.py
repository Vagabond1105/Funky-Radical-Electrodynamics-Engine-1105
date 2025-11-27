# below is physics_engine.py

# necessary imports

import pygame
import numpy as np
from constants_for_all_files import *

# Physics Engine for Point Charge Dynamics

# constants for physics calculations

dt = 1/9000

# Physics Engine Class

class PhysicsEngine:

    def __init__(self):
        pass

    # acceleration due to electric forces

    def get_accelerations(self, positions, velocities, charges, masses, static_status):

        # Calculates net accerlation for each point charge due to electric forces from all other charges
        # Returns an array of shape (N, 2) where N is number of point charges and each row is the acceleration vector [ax, ay]

        n = len(positions)
        accelerations = np.zeros((n, 2), dtype=float)

        if n < 2:
            return accelerations
        
        # n body coloumb loop: O(N^2)
        for i in range(n):
            if static_status[i]:
                continue # skip static charges for acceleration calculation
            
            net_force = np.array([0.0, 0.0], dtype=float)

            for j in range(n):
            
                if i == j:
                    continue # skip self-interaction

                diff = positions[j] - positions[i]
                r2 = np.dot(diff, diff)

                if r2 < 400: # minimum distance squared to avoid extreme forces
                    r2 = 400

                # Use vector from j to i so like charges repel (Coulomb: F_i = k*q_i*q_j*(r_i - r_j)/r^3)
                # diff currently is r_j - r_i, so invert it to get r_i - r_j
                diff_ij = -diff
                r = np.sqrt(r2)
                force_magnitude = (K_COULOMB * charges[i] * charges[j]) / r2
                direction = diff_ij / r
                force = force_magnitude * direction
                net_force += force

            # acceleration = net_force / mass
            accelerations[i] += net_force / masses[i]

        return accelerations
    
    # updates positions and velocities of point charges

    def update_positions_velocities(self, dt, all_charges):

        # does RK4 integration to update positions and velocities of all point charges

        n = len(all_charges)
        if n == 0:
            return
        
        # use a bunch of arrays lol brrr ARRRGH OOPHH

        positions = np.array([p.position for p in all_charges])
        velocities = np.array([p.vel for p in all_charges])
        charges = np.array([p.charge for p in all_charges])
        masses = np.array([p.mass for p in all_charges])
        static_status = np.array([p.static for p in all_charges], dtype=bool)

        # RK4 Integration Steps

        # state at t
        a1 = self.get_accelerations(positions, velocities, charges, masses, static_status)
        v1 = velocities

        # state at t + dt/2
        p2 = positions + 0.5 * dt * v1
        v2 = velocities + 0.5 * dt * a1
        a2 = self.get_accelerations(p2, v2, charges, masses, static_status)

        # state at t + dt/2 using _2 slopes

        p3 = positions + 0.5 * dt * v2
        v3 = velocities + 0.5 * dt * a2
        a3 = self.get_accelerations(p3, v3, charges, masses, static_status)

        # state at t + dt using _3 slopes

        p4 = positions + dt * v3
        v4 = velocities + dt * a3
        a4 = self.get_accelerations(p4, v4, charges, masses, static_status)

        # combine it all

        new_positions = positions + (dt / 6.0) * (v1 + 2 * v2 + 2 * v3 + v4)
        new_velocities = velocities + (dt / 6.0) * (a1 + 2 * a2 + 2 * a3 + a4)

        # now all the new positions and velocities are updated for the point charges

        for i in range(n):
            if not static_status[i]:
                all_charges[i].position = new_positions[i]
                all_charges[i].vel = new_velocities[i]

    def handle_wall_collisions(self, all_charges, wall_cor):
        """Checks and resolves collisions with the screen boundaries."""
        for pc in all_charges:
            if pc.static: continue

            # X Axis (Left/Right)
            left_bound = WALL_INNER_RECT.left + pc.total_radius
            right_bound = WALL_INNER_RECT.right - pc.total_radius
            if pc.position[0] < left_bound:
                pc.position[0] = left_bound
                pc.vel[0] *= -wall_cor
            elif pc.position[0] > right_bound:
                pc.position[0] = right_bound
                pc.vel[0] *= -wall_cor
                
            # Y Axis (Top/Bottom)
            top_bound = WALL_INNER_RECT.top + pc.total_radius
            bottom_bound = WALL_INNER_RECT.bottom - pc.total_radius
            if pc.position[1] < top_bound:
                pc.position[1] = top_bound
                pc.vel[1] *= -wall_cor
            elif pc.position[1] > bottom_bound:
                pc.position[1] = bottom_bound
                pc.vel[1] *= -wall_cor

    def handle_particle_collisions(self, all_charges):

        """Checks and resolves elastic collisions between all particle pairs."""
        n = len(all_charges)
        # O(N^2) loop, but clean
        for i in range(n):
            for j in range(i + 1, n):
                p1 = all_charges[i]
                p2 = all_charges[j]
                p1.resolve_collision(p2)