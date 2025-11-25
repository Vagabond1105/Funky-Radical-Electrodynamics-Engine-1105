import pygame
import sys
import numpy as np

# IMPORTS
from constants_for_all_files import *
from point_charges import PointCharge
from electric_field import ElectricFieldSystem
from gui import ResetButton, StartButton, ContextMenu, CreationForm, WallCORSlider

# --- 1. INITIALIZATION & SETUP ---
pygame.init()
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("FREE1105: Phase 1 - Setup & Initialization")
clock = pygame.time.Clock()

# --- 2. SYSTEMS ---
ef_system = ElectricFieldSystem()
reset_btn = ResetButton()
pause_btn = PauseButton()
start_btn = StartButton()
context_menu = ContextMenu()
create_form = CreationForm()
# Slider positioned near the wall constants
wall_cor_slider = WallCORSlider(30, 20, 150, 30, initial_value=BW_coeff)

# --- 3. STATE MANAGEMENT ---
# 0 = SETUP (Edit Mode), 1 = RUNNING (Physics Mode)
sim_state = 0 

all_point_charges = []
selected_charge = None
p_id_counter = 0
wall_cor = wall_cor_slider.value 

# --- 4. THE SIMULATION LOOP ---

running = True
while running:
    
    # --- A. TIME & MOUSE ---
    dt = clock.tick(60) / 1000.0 # Delta Time
    mouse_pos = pygame.mouse.get_pos()
    
    # --- B. GLOBAL EVENT HANDLING (THE ONE TRUE LOOP) ---
    for event in pygame.event.get():
        # 1. GLOBAL: Quit
        if event.type == pygame.QUIT:
            running = False
        
        # 2. GLOBAL: Reset Button (Works in ANY state to save you)
        if reset_btn.handle_event(event):
            sim_state = 0 # Force back to SETUP
            # Keep only environmental charges
            all_point_charges = [pc for pc in all_point_charges if pc.environmental]
            # Reset their positions
            for pc in all_point_charges:
                pc.reset()
            print("SIMULATION RESET")

        # --- C. STATE SPECIFIC EVENTS ---
        
        # === STATE 0: SETUP PHASE (Editing Allowed) ===
        if sim_state == 0:
            
            # 1. Start Button (Only works in Setup) and requires no particles touching walls or other particles and they are existing
            particles_touching = False
            for pc in all_point_charges:
                if (pc.position[0] - pc.total_radius <= 0 or
                    pc.position[0] + pc.total_radius >= SW or
                    pc.position[1] - pc.total_radius <= 0 or
                    pc.position[1] + pc.total_radius >= SH):
                    particles_touching = True
                    break
                for other_pc in all_point_charges:
                    if other_pc != pc:
                        dist = np.linalg.norm(pc.position - other_pc.position)
                        if dist < (pc.total_radius + other_pc.total_radius):
                            particles_touching = True
                            break
                if particles_touching:
                    break

            if start_btn.handle_event(event) and not particles_touching and len[all_point_charges] > 0:
                sim_state = 1 # LOCK IN! Switch to Running
                # Clear any active selections
                selected_charge = None
                context_menu.active = False
                create_form.active = False
                print("SIMULATION STARTED")
            elif start_btn.handle_event(event) and particles_touching:
                print("ERROR: Cannot start simulation while particles are touching walls or each other.")
            elif start_btn.handle_event(event) and len(all_point_charges) == 0:
                print("ERROR: Cannot start simulation without any point charges present.")

            # 2. Wall Slider
            wall_cor_slider.handle_event(event)

            # 3. Context Menu Logic
            menu_action = context_menu.handle_event(event)
            if menu_action == "open_creator":
                create_form.show(context_menu.pos)

            # 4. Creation Form Logic
            form_data = create_form.handle_event(event)
            if form_data:
                try:
                    if form_data.get('edit'):
                        # Edit existing particle
                        particle = form_data['particle']
                        particle.charge = form_data['charge']
                        particle.mass = form_data['mass']
                        particle.environmental = form_data['environmental']
                        particle.static = form_data['static']
                        particle.color = (200, 0, 0) if particle.charge > 0 else (0, 0, 200)
                        particle.update_relative_scale(all_point_charges)
                    else:
                        # Create new particle
                        new_pc = PointCharge(
                            pos_0=form_data['position'],
                            charge=form_data['charge'],
                            mass=form_data['mass'],
                            environmental=form_data['environmental'],
                            static=form_data['static'],
                            pc_id=p_id_counter
                        )
                        all_point_charges.append(new_pc)
                        p_id_counter += 1
                except Exception as e:
                    print(f"Form Error: {e}")

            # 5. Mouse Interactions (Drag & Drop / Right Click)
            # Only allowed if GUI is NOT blocking the mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not context_menu.active and not create_form.active and not wall_cor_slider.dragging:
                    
                    if event.button == 1: # Left Click (Select/Drag)
                        for pc in reversed(all_point_charges):
                            dist = np.linalg.norm(pc.position - np.array(event.pos))
                            if dist < pc.total_radius:
                                selected_charge = pc
                                pc.dragging = True
                                break
                                
                    elif event.button == 3: # Right Click (Context Menu)
                        clicked_on_charge = False
                        clicked_charge = None
                        for pc in reversed(all_point_charges):
                             dist = np.linalg.norm(pc.position - np.array(event.pos))
                             if dist < pc.total_radius:
                                 clicked_on_charge = True
                                 clicked_charge = pc
                                 break
                        
                        if clicked_on_charge:
                            create_form.show(event.pos, particle=clicked_charge)
                        else:
                            context_menu.show(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and selected_charge:
                    selected_charge.dragging = False
                    selected_charge = None
                    
            elif event.type == pygame.MOUSEMOTION:
                if selected_charge:
                    selected_charge.position = np.array(event.pos, dtype=float)

        # === STATE 1: RUNNING PHASE (Physics Allowed) ===
        elif sim_state == 1:
            # No dragging allowed here!
            # Just listening for "Pause" (Future Phase) or "Reset" (Global)

            if pause_btn.handle_event(event):
                sim_state = 0.5 # Literally just pauses the sim

            if reset_btn.handle_event(event):
                sim_state = 0

                # keep only environmental charges and reverts everything to their initial state

                all_point_charges = [pc for pc in all_point_charges if pc.environmental]
                for pc in all_point_charges:
                    pc.reset()

        elif sim_state == 0.5:

            # Paused State - Listen for Unpause from same button or Reset
            if pause_btn.handle_event(event):
                sim_state = 1 # Resume Simulation

            if reset_btn.handle_event(event):
                sim_state = 0

                # keep only environmental charges and reverts everything to their initial state

                all_point_charges = [pc for pc in all_point_charges if pc.environmental]
                for pc in all_point_charges:
                    pc.reset()

    # --- D. LOGIC UPDATES (General) ---
    
    # Update wall coefficient
    wall_cor = wall_cor_slider.value 

    # Update visual scales (Always needed for rendering)
    for pc in all_point_charges:
        pc.update_relative_scale(all_point_charges)

    # --- E. PHYSICS UPDATES (State Dependent) ---
    if sim_state == 1:
        # This is where we will put the RK4 Integrator and Collision logic
        # for pc in all_point_charges:
        #     pc.update_physics(dt, all_point_charges, wall_cor)
        pass

    # --- F. RENDERING (The Layers) ---
    
    # Layer 0: Background (E-Field)
    ef_system.render(screen, all_point_charges)
    
    # Layer 1: Environment (Walls)
    pygame.draw.rect(screen, WC, WALL_RECT, BT) 
    
    # Layer 2: Particles
    for pc in all_point_charges:
        pc.render(screen)

    # Layer 3: GUI (State Dependent)
    # Always show Reset
    reset_btn.render(screen)
    
    if sim_state == 0:
        # Only show Setup GUI in Setup Mode
        start_btn.render(screen)
        reset_btn.render(screen)
        wall_cor_slider.render(screen)
        context_menu.render(screen)
        create_form.render(screen)
    elif sim_state == 1:
        reset_btn.render(screen)
        pause_btn.render(screen)
        pass

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()