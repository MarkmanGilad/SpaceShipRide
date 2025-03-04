import pygame

class Human_Agent:
    def __init__ (self):
        self.action = 0
        

    def get_action (self, state = None):
        keys = pygame.key.get_pressed()
        F_thrust = 0
        T_spin = 0
        if keys[pygame.K_UP]:
            F_thrust = 0.5  # Apply continuous forward thrust
        if keys[pygame.K_RIGHT]:
            T_spin = -0.5  # Clockwise rotation
        if keys[pygame.K_LEFT]:
            T_spin = 0.5   # Counter-clockwise rotation
        return F_thrust, T_spin
    

