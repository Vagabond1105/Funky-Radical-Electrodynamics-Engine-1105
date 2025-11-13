import numpy as np
import pygame
import sys

# the set up

pygame.init() # initialises pygame
sw = 1500 # screen width
sh = 900 # screen height
bgc = (200,200,200) # background colour
wc = (0,0,0) # wall colour
bt = 20 # wall border thickness
bw_coeff = 1 # border wall elasticity coefficient

screen = pygame.display.set_mode((sw,sh)) # shows up the screen
pygame.display.set_caption("FREE: Phase 1") # sets a caption for the window
clock = pygame.time.Clock() # clock to cap fps

# the components go here

class dropdown_menu:

    options_list = ["Point Charges"]

    def __init__(self, position, width, height_per_option, options_list, selected = 0):
        self.position = position
        self.width = width
        self.height_per_option = height_per_option
        self.options_list = options_list
        self.selected = selected
        self.expanded = False
        self.last_triggered = None
        self.hovered_option = None
        self.font = pygame.font.SysFont('Console', 14)

    def render_menu(self, screen):
        if self.expanded:
            for i in range(len(self.options_list)):
                # grey background if hovering
                bg_color = (220, 220, 220) if i == self.hovered_option else (255, 255, 255)
                pygame.draw.rect(screen, bg_color, (self.position[0], self.position[1] + i*self.height_per_option, self.width, self.height_per_option))
                pygame.draw.rect(screen, (0, 0, 0), (self.position[0], self.position[1] + i*self.height_per_option, self.width, self.height_per_option), 2)
                option_text = self.font.render(self.options_list[i], True, (0, 0, 0))
                screen.blit(option_text, (self.position[0] + 5, self.position[1] + i*self.height_per_option + 5))

    def update_hover(self, mouse_pos):
        """Update which option is hovered based on mouse position."""
        if self.expanded:
            self.hovered_option = None
            for i in range(len(self.options_list)):
                option_rect = pygame.Rect(self.position[0], self.position[1] + i*self.height_per_option, self.width, self.height_per_option)
                if option_rect.collidepoint(mouse_pos):
                    self.hovered_option = i
                    break

    def handle_event(self, event, mouse_pos):
        """Handle click event on menu. Returns True if an option was selected."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                if self.expanded:
                    for i in range(len(self.options_list)):
                        option_rect = pygame.Rect(self.position[0], self.position[1] + i*self.height_per_option, self.width, self.height_per_option)
                        if option_rect.collidepoint(mouse_pos):
                            self.selected = i
                            self.last_triggered = i
                            self.expanded = False
                            self.hovered_option = None
                            return True
                    # clicked outside menu: close it
                    self.expanded = False
                    self.hovered_option = None
        return False

    def close(self):
        """Close the menu."""
        self.expanded = False
        self.hovered_option = None
        self.last_triggered = None

dropdown_menu_rc = dropdown_menu(np.array([-1000, -1000]), 120, 30, dropdown_menu.options_list)

class TextBox:
    """Simple text input box that filters input."""
    def __init__(self, x, y, width, height, label, allow_negative=True, allow_float=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.text = ""
        self.active = False
        self.allow_negative = allow_negative
        self.allow_float = allow_float
        self.font = pygame.font.SysFont('Console', 14)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                char = event.unicode
                # allow digits
                if char.isdigit():
                    self.text += char
                # allow minus sign at start or if allowed
                elif char == '-' and self.allow_negative and (not self.text or self.text[0] != '-'):
                    self.text = '-' + self.text
                # allow decimal point if allowed and not already present
                elif char == '.' and self.allow_float and '.' not in self.text:
                    self.text += char
    
    def get_value(self):
        """Return the numeric value, or None if invalid."""
        if not self.text:
            return None
        try:
            if self.allow_float:
                return float(self.text)
            else:
                return int(self.text)
        except ValueError:
            return None
    
    def render(self, screen):
        # draw label
        label_surf = self.font.render(self.label, True, (0, 0, 0))
        screen.blit(label_surf, (self.rect.x, self.rect.y - 20))
        
        # draw box
        color = (100, 100, 255) if self.active else (200, 200, 200)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        # draw text
        text_surf = self.font.render(self.text if self.text else "", True, (0, 0, 0))
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

class Toggle:
    """Simple toggle button (on/off)."""
    def __init__(self, x, y, label, initial_state=True):
        self.rect = pygame.Rect(x, y, 50, 25)
        self.label = label
        self.state = initial_state
        self.font = pygame.font.SysFont('Console', 12)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state
    
    def render(self, screen):
        # draw label
        label_surf = self.font.render(self.label, True, (0, 0, 0))
        screen.blit(label_surf, (self.rect.x, self.rect.y - 20))
        
        # draw toggle box
        color = (100, 200, 100) if self.state else (200, 100, 100)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        # draw text
        text = "ON" if self.state else "OFF"
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class PointChargeForm:
    """Form for creating a new point charge."""
    def __init__(self, position, width=400, height=220):
        self.rect = pygame.Rect(position[0], position[1], width, height)
        self.visible = False
        self.font = pygame.font.SysFont('Console', 14)
        
        # text boxes for charge and mass
        self.charge_box = TextBox(self.rect.x + 20, self.rect.y + 60, 80, 25, "Charge", allow_negative=True, allow_float=True)
        self.mass_box = TextBox(self.rect.x + 100, self.rect.y + 60, 80, 25, "Mass", allow_negative=False, allow_float=True)
        
        # toggles for environmental and static
        self.environmental_toggle = Toggle(self.rect.x + 20, self.rect.y + 100, "Environmental", initial_state=True)
        self.static_toggle = Toggle(self.rect.x + 120, self.rect.y + 100, "Static", initial_state=True)
        
        # submit/cancel buttons
        self.submit_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 160, 80, 25)
        self.cancel_rect = pygame.Rect(self.rect.x + 120, self.rect.y + 160, 80, 25)
    
    def handle_event(self, event):
        """Handle events. Returns tuple (action, data) where action is 'submit', 'cancel', or None."""
        self.charge_box.handle_event(event)
        self.mass_box.handle_event(event)
        self.environmental_toggle.handle_event(event)
        self.static_toggle.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.submit_rect.collidepoint(event.pos):
                charge_val = self.charge_box.get_value()
                mass_val = self.mass_box.get_value()
                if charge_val is not None and mass_val is not None:
                    return ('submit', {
                        'charge': charge_val,
                        'mass': mass_val,
                        'environmental': self.environmental_toggle.state,
                        'static': self.static_toggle.state
                    })
            elif self.cancel_rect.collidepoint(event.pos):
                return ('cancel', None)
        
        return (None, None)
    
    def render(self, screen):
        if not self.visible:
            return
        
        # draw background
        pygame.draw.rect(screen, (240, 240, 240), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 3)
        
        # draw title
        title = self.font.render("Create Point Charge", True, (0, 0, 0))
        screen.blit(title, (self.rect.x + 10, self.rect.y + 10))
        
        # render controls
        self.charge_box.render(screen)
        self.mass_box.render(screen)
        self.environmental_toggle.render(screen)
        self.static_toggle.render(screen)
        
        # render buttons
        pygame.draw.rect(screen, (100, 200, 100), self.submit_rect)
        pygame.draw.rect(screen, (0, 0, 0), self.submit_rect, 2)
        submit_text = self.font.render("Submit", True, (0, 0, 0))
        screen.blit(submit_text, (self.submit_rect.x + 5, self.submit_rect.y + 5))
        
        pygame.draw.rect(screen, (200, 100, 100), self.cancel_rect)
        pygame.draw.rect(screen, (0, 0, 0), self.cancel_rect, 2)
        cancel_text = self.font.render("Cancel", True, (0, 0, 0))
        screen.blit(cancel_text, (self.cancel_rect.x + 5, self.cancel_rect.y + 5))
    
    def show_at(self, position):
        """Show the form at a given position."""
        self.rect.topleft = position
        self.charge_box.rect.topleft = (self.rect.x + 20, self.rect.y + 40)
        self.mass_box.rect.topleft = (self.rect.x + 150, self.rect.y + 40)
        self.environmental_toggle.rect.topleft = (self.rect.x + 20, self.rect.y + 100)
        self.static_toggle.rect.topleft = (self.rect.x + 220, self.rect.y + 100)
        self.submit_rect.topleft = (self.rect.x + 20, self.rect.y + 160)
        self.cancel_rect.topleft = (self.rect.x + 120, self.rect.y + 160)
        
        # reset fields
        self.charge_box.text = "1.0"
        self.mass_box.text = "1.0"
        self.charge_box.active = False
        self.mass_box.active = False
        self.environmental_toggle.state = True
        self.static_toggle.state = True
        
        self.visible = True
    
    def hide(self):
        """Hide the form."""
        self.visible = False

class PointCharge:

    e_charge = 1.602e-19 # elementary charge in coulombs
    e_mass = 9.109e-31 # electron mass in kg

    def __init__(self, charge, mass, position, velocity, environmental, static):
    
        self.charge = charge * PointCharge.e_charge
        self.mass = mass * PointCharge.e_mass
        self.position = np.array([position[0], position[1]]) 
        # accept velocity as a sequence or pair
        self.velocity = np.array([velocity[0], velocity[1]])
        if self.charge > 0:
            self.colour = (255,0,0)
        elif self.charge < 0:
            self.colour = (0,0,255)
        else:
            self.colour = (0,0,0)
        self.radius = 30
        self.border = self.radius + 6 
        self.environmental = environmental
        self.static = static

    @staticmethod
    def get_radius_from_charge(point_charge, all_point_charges=None): # calculates radius based on relative charge magnitude
        if all_point_charges is None:
            all_point_charges = []

        weakest_charge_magnitude = float('inf')
        strongest_charge_magnitude = 0

        for pc in all_point_charges:
            charge_magnitude = abs(pc.charge)
            if charge_magnitude < weakest_charge_magnitude:
                weakest_charge_magnitude = charge_magnitude
            if charge_magnitude > strongest_charge_magnitude:
                strongest_charge_magnitude = charge_magnitude

        # if all charges equal or no other charges, return default radius
        if strongest_charge_magnitude == weakest_charge_magnitude:
            return 10

        radius = 10 + 40 * (1 - (strongest_charge_magnitude - abs(point_charge.charge)) / (strongest_charge_magnitude - weakest_charge_magnitude))
        return max(4, radius)

    @staticmethod
    def get_border_from_mass(point_charge, all_point_charges=None): # calculates border thickness based on relative mass magnitude
        if all_point_charges is None:
            all_point_charges = []

        lightest_mass_magnitude = float('inf')
        heaviest_mass_magnitude = 0

        for pc in all_point_charges:
            mass_magnitude = abs(pc.mass)
            if mass_magnitude < lightest_mass_magnitude:
                lightest_mass_magnitude = mass_magnitude
            if mass_magnitude > heaviest_mass_magnitude:
                heaviest_mass_magnitude = mass_magnitude

        if heaviest_mass_magnitude == lightest_mass_magnitude:
            return 2

        border = 2 + 8 * (1 - (heaviest_mass_magnitude - abs(point_charge.mass)) / (heaviest_mass_magnitude - lightest_mass_magnitude))
        return max(1, border)

    @staticmethod
    def determine_pc_size(point_charge, all_point_charges=None):
        if all_point_charges is None:
            all_point_charges = []

        point_charge.radius = PointCharge.get_radius_from_charge(point_charge, all_point_charges)
        point_charge.border = PointCharge.get_border_from_mass(point_charge, all_point_charges)

    def render_pc(self, screen): # draws the black circle first and then the coloured circle on top to create a border effect

        pygame.draw.circle(screen, (0,0,0), (int(self.position[0]), int(self.position[1])), self.border) # draws the border
        pygame.draw.circle(screen, self.colour, (int(self.position[0]), int(self.position[1])), self.radius) # draws the point charge

class ResetButton:
    """Reset button to clear all non-environmental point charges."""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.hovered = False
        self.font = pygame.font.SysFont('Montserrat', 20)
    
    def update_hover(self, mouse_pos):
        """Update hover state."""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def handle_event(self, event):
        """Handle click event. Returns True if clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False
    
    def render(self, screen):
        """Render the button with hover effect."""
        # darker red when hovered, lighter red when not
        color = (100, 50, 50) if self.hovered else (255, 140, 140)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 3)
        
        # render text
        text_color = (200, 200, 200) if self.hovered else (100, 100, 100)
        text_surf = self.font.render("RESET", True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

# the simulation loop where basically EVERYTHING runs

def run_simulation():
    all_point_charges = [] # list to hold all point charges
    form = PointChargeForm((sw // 2 - 200, sh // 2 - 100))
    reset_button = ResetButton(10, sh - 40, 100, 30)  # bottom left corner
    menu_pos = None  # position where menu was opened

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # update dropdown hover state
        if dropdown_menu_rc.expanded:
            dropdown_menu_rc.update_hover(mouse_pos)
        
        # update reset button hover state
        reset_button.update_hover(mouse_pos)

        for event in pygame.event.get(): # where inputs are read during run time

            if event.type == pygame.QUIT: # allows you to close the window by clicking the x on the corner
                running = False
            
            # handle reset button click
            if reset_button.handle_event(event):
                # remove all non-environmental charges
                all_point_charges = [pc for pc in all_point_charges if pc.environmental]
            
            # handle form input if visible
            if form.visible:
                action, data = form.handle_event(event)
                if action == 'submit' and data:
                    # create a new point charge with form data
                    pos = menu_pos if menu_pos else (sw // 2, sh // 2)
                    new_point_charge = PointCharge(
                        charge=data['charge'],
                        mass=data['mass'],
                        position=pos,
                        velocity=[0, 0],
                        environmental=data['environmental'],
                        static=data['static']
                    )
                    all_point_charges.append(new_point_charge)
                    form.hide()
                elif action == 'cancel':
                    form.hide()
            else:
                # handle dropdown and right-click menu
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # left click
                        # close dropdown if clicking outside it
                        if dropdown_menu_rc.expanded:
                            menu_rect = pygame.Rect(
                                dropdown_menu_rc.position[0],
                                dropdown_menu_rc.position[1],
                                dropdown_menu_rc.width,
                                len(dropdown_menu_rc.options_list) * dropdown_menu_rc.height_per_option
                            )
                            if not menu_rect.collidepoint(mouse_pos):
                                dropdown_menu_rc.close()
                            else:
                                # clicked on menu: handle selection
                                option_selected = dropdown_menu_rc.handle_event(event, mouse_pos)
                                if option_selected and dropdown_menu_rc.last_triggered is not None:
                                    idx = dropdown_menu_rc.last_triggered
                                    opt = dropdown_menu_rc.options_list[idx]
                                    dropdown_menu_rc.last_triggered = None
                                    if opt == "Point Charges":
                                        # show form at menu position
                                        menu_pos = (int(dropdown_menu_rc.position[0]), int(dropdown_menu_rc.position[1]))
                                        form.show_at(menu_pos)
                    
                    elif event.button == 3:  # right click
                        # only open menu if clicking empty space
                        clicked_on_pc = False
                        for pc in all_point_charges:
                            if np.linalg.norm(pc.position - np.array(mouse_pos)) <= pc.border:
                                clicked_on_pc = True
                                break
                        if not clicked_on_pc:
                            # position menu at click, keep it on-screen
                            x = mouse_pos[0]
                            y = mouse_pos[1]
                            if x + dropdown_menu_rc.width > sw:
                                x = sw - dropdown_menu_rc.width
                            total_h = dropdown_menu_rc.height_per_option * len(dropdown_menu_rc.options_list)
                            if y + total_h > sh:
                                y = sh - total_h
                            dropdown_menu_rc.position = np.array([x, y])
                            dropdown_menu_rc.expanded = True
                            menu_pos = (int(x), int(y))

        # where the physics, logic and calculations go below to update components

        screen.fill(bgc) # reclears the screen
        pygame.draw.rect(screen, wc, (0,0,sw,bt)) # top wall
        pygame.draw.rect(screen, wc, (0,sh-bt,sw,bt)) # bottom wall
        pygame.draw.rect(screen, wc, (0,0,bt,sh)) # left wall
        pygame.draw.rect(screen, wc, (sw-bt,0,bt,sh)) # right wall

        # where the updated screen is re rendered below with all the components

        for pc in all_point_charges: # assuming all_point_charges is a list or array of PointCharge objects
            PointCharge.determine_pc_size(pc, all_point_charges)
            pc.render_pc(screen)

        # render dropdown menu every frame (if expanded it'll show)
        dropdown_menu_rc.render_menu(screen)
        
        # render form every frame (if visible it'll show)
        form.render(screen)
        
        # render reset button
        reset_button.render(screen)

        pygame.display.flip() # updates the screen
        clock.tick(60) # caps fps to 60 like pc master race

    pygame.quit()


if __name__ == "__main__":
    run_simulation()