import pygame
import math

# Global constants
WIDTH, HEIGHT = 800, 600
FPS = 60
LIGHTGRAY = (200, 200, 200)

import pygame
import math

# Global constants
WIDTH, HEIGHT = 800, 600
FPS = 60
LIGHTGRAY = (200, 200, 200)

class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, image, pos = (700, 500)) -> None:
        super().__init__()
        self.original_image = image  # Unrotated copy for proper rotation
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.radius = 30
        self.mask = pygame.mask.from_surface(self.image)
        self.start_pos = (700, 500)
        # Define theta relative to up (0 means facing up)
        self.centerx, self.centery = self.start_pos
        self.theta = 0  
        self.vx = 0
        self.vy = 0
        self.omega = 0  # Angular velocity
        
        self.max_thrust = 100
        self.max_spin = 3

    def move(self, dt, F_thrust, T_spin):
        # Update angular velocity and angle
        self.omega = self.max_spin * T_spin
        self.theta += self.omega * dt

        # Compute acceleration based on the corrected forward vector
        ax = - (self.max_thrust * F_thrust) * math.sin(self.theta)
        ay = - (self.max_thrust * F_thrust) * math.cos(self.theta)

        # Update velocity
        self.vx += ax * dt
        self.vy += ay * dt

        # Update position
        dx = self.vx * dt
        dy = self.vy * dt

        self.centerx += dx
        self.centery += dy

        self.rect.centerx = round(self.centerx)
        self.rect.centery = round(self.centery)
        

        # Rotate the image to match the current theta
        rotated_image = pygame.transform.rotate(self.original_image, math.degrees(self.theta))
        self.image = rotated_image
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self, dt, F_thrust, T_spin):
        self.move(dt, F_thrust, T_spin)

    def restart(self):
        self.theta = 0  
        self.vx = 0
        self.vy = 0
        self.omega = 0  # Angular velocity
        self.centerx, self.centery = self.start_pos