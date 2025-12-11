
# below is the main.py file

# necessary imports

import pygame
import numpy as np
import sys

# import all other necessary modules

from constants_for_all_files_jypter1 import *
from point_charges_jypter1 import *
from electric_field_jypter1 import *
from gui_jypter1 import *

# set up the window

pygame.init()
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("FREE1105: Phase 1")
clock = pygame.time.Clock()

# setting up systems

ef_system = ElectricFieldSystem()
reset_btn = ResetButton()
context_menu = ContextMenu()
create_form = CreationForm()
start_btn = StartButton()
wall_cor_slider = WallCORSlider(30, 20, 150, 30, initial_value=BW_coeff)

# setting up initial state of the simulation

all_point_charges = []
selected_charge = None
p_id_counter = 0
wall_cor = wall_cor_slider.value  # Current wall coefficient of restitution

# the main loop where everything happens

running = True
while running:

    # event handling

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        # handle reset button

        if reset_btn.handle_event(event):
            all_point_charges = [pc for pc in all_point_charges if pc.environmental]
            for pc in all_point_charges:
                pc.reset()

        # handle start button

        if start_btn.handle_event(event):
            pass  # TODO: Start simulation logic

        # handle wall COR slider

        wall_cor_slider.handle_event(event)

        # handle context menu

        menu_action = context_menu.handle_event(event)
        if menu_action == "open_creator":
            create_form.show(context_menu.pos)

        # creation/edit form handling

        form_data = create_form.handle_event(event)
        if form_data:
            try:
                if form_data.get('edit'):
                    # Edit mode: update existing particle
                    particle = form_data['particle']
                    particle.charge = form_data['charge']
                    particle.mass = form_data['mass']
                    particle.environmental = form_data['environmental']
                    particle.static = form_data['static']
                    # Update color based on new charge sign
                    particle.color = (200, 0, 0) if particle.charge > 0 else (0, 0, 200)
                    particle.update_relative_scale(all_point_charges)
                    print(f"EDIT: Particle updated - charge={particle.charge}, mass={particle.mass}, env={particle.environmental}, static={particle.static}")
                else:
                    # Create mode: spawn new particle
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
                import traceback
                print("Error in form submission:")
                print("form_data=", form_data)
                traceback.print_exc()

        # mouse interactions

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Click (Drag)
                if not context_menu.active and not create_form.active:
                    for pc in reversed(all_point_charges):
                        # Check distance for click
                        dist = np.linalg.norm(pc.position - np.array(event.pos))
                        if dist < pc.total_radius:
                            selected_charge = pc
                            pc.dragging = True
                            break

            elif event.button == 3: # Right Click (Menu or Edit)
                clicked_on_charge = False
                clicked_charge = None
                for pc in reversed(all_point_charges):
                     dist = np.linalg.norm(pc.position - np.array(event.pos))
                     if dist < pc.total_radius:
                         # Right clicked a charge - open edit form
                         clicked_on_charge = True
                         clicked_charge = pc
                         break

                if clicked_on_charge and clicked_charge:
                    # Open edit form for this charge
                    create_form.show(event.pos, particle=clicked_charge)
                else:
                    # Open context menu to create new charge
                    context_menu.show(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and selected_charge:
                selected_charge.dragging = False
                selected_charge = None

        elif event.type == pygame.MOUSEMOTION:
            if selected_charge:
                selected_charge.position = np.array(event.pos, dtype=float)

    # logic and updates

    wall_cor = wall_cor_slider.value  # Update wall coefficient from slider

    for pc in all_point_charges:
        pc.update_relative_scale(all_point_charges)

    # rendering

    ef_system.render(screen, all_point_charges)
    pygame.draw.rect(screen, WC, WALL_RECT, WBT) # draw wall
    for pc in all_point_charges:
        pc.render(screen)

    # gui rendering

    reset_btn.render(screen)
    start_btn.render(screen)
    wall_cor_slider.render(screen)
    context_menu.render(screen)
    create_form.render(screen)

    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()
sys.exit()
