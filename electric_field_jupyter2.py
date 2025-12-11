
# below is electric_field.py file

# necessary imports

import pygame
import numpy as np
from constants_for_all_files import *

# Electric Field Calculation and Visualization

class ElectricFieldSystem:

    def __init__(self):

        # sets up the virtual grid

        self.x_coords = np.linspace(0, SW, V_SW)
        self.y_coords = np.linspace(0, SH, V_SH)
        self.grid_x, self.grid_y = np.meshgrid(self.x_coords, self.y_coords)

        # surface to hold the heatmap

        self.surface = pygame.Surface((V_SW, V_SH))

    def render(self, target_surface, charges):

        if not charges:
            target_surface.fill(BGC)
            return

        # Calculate the electric field at each grid point due to all charges

        net_field = np.zeros_like(self.grid_x, dtype=float)

        for pc in charges:
            dx = self.grid_x - pc.position[0]
            dy = self.grid_y - pc.position[1]
            r2 = dx**2 + dy**2
            r2[r2 == 0] = E_CHARGE # Prevent division by zero
            min_distance = pc.total_radius ** 2
            r2[r2 < min_distance] = min_distance # Cap minimum distance squared to avoid extreme values

            contribution = (K_COULOMB * pc.charge) / r2
            net_field += contribution

        # colourises the heatmap based on field strength

        max_val = np.max(np.abs(net_field))
        if max_val == 0:
            max_val = 100  # so eveything is neutral grey

        normalised = 0.7 * net_field / max_val
        pixel_vals = 127.5 - (normalised * 127.5)
        pixel_vals = np.clip(pixel_vals, 0, 255).astype(np.uint8)

        # create RGB array for Pygame surface

        pixels = np.dstack([pixel_vals] * 3)
        pygame.surfarray.blit_array(self.surface, np.swapaxes(pixels, 0, 1))

        # scale up to full screen

        scaled_view = pygame.transform.scale(self.surface, (SW, SH))
        target_surface.blit(scaled_view, (0, 0))

