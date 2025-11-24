# below is constants_for_all_files.py

# necessary imports

import pygame
import numpy as np

# dimensions

SW = 1500 # Screen Width
SH = 900  # Screen Height
# (1/4 scale for E-Field calc) then scale up for perfomance
V_SW = SW // 4 # Virtual Width 
V_SH = SH // 4 # Virtual Height 

# default colors + wall stuff

BGC = 128, 128, 128  # Background Color for Neutral Grey
WC = (0,0, 0) # Neon Green for Wall Color
text_c = (30,30, 30) # Dark Grey for Text Color
WALL_RECT = pygame.Rect(0, 0, SW, SH)

# physics constants

WBT = 20 # Wall Border Thickness
BW_coeff = 0.9 # Coefficient of Restitution for Bouncing Wall
K_COULOMB = 8.99e9 # Coulomb's Constant in N m²/C²
E_CHARGE = 1.602e-19 # Elementary Charge in Coulombs
E_MASS = 9.109e-31 # Electron Mass in kg
P_MASS = 1.672e-27 # Proton Mass in kg