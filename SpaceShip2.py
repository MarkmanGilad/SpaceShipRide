import pygame
import math
from Graphics import *


class SpaceShip(pygame.sprite.Sprite):

    img = pygame.image.load("img/spacecraft.png")
    img = pygame.transform.rotate(img, 270)

    def __init__(self, pos=(700, 500), size = (50,50)) -> None:
        super().__init__()
        self.original_image = pygame.transform.scale(SpaceShip.img, size)  # Unrotated copy for proper rotation
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        self.radius = max(size[0], size[1]) // 2
        self.mask = pygame.mask.from_surface(self.image)
        self.start_pos = pos

        # Position and rotation
        self.centerx, self.centery = self.start_pos
        self.theta = 0 
        
        # Velocity and angular velocity
        self.vx = 0
        self.vy = 0
                
        # Limits
        self.max_acc = 1         # max acceleration pixels per frame^2
        self.max_spin = (2 * math.pi ) / 24 # maximum spin per frame
        self.v_opt = 2   # pixels per frame

        # Friction parameters
        self.friction = 0.05  # linear slow down friction
        
        # Fuel system
        self.max_fuel = 1000
        self.fuel = self.max_fuel
        
        

    def move(self, thrust, spin):
        if self.fuel > 0:
            # Update angular velocity and apply friction
            self.theta += self.max_spin * spin
            self.theta %= (2 * math.pi)         # Keep theta in [0, 2*pi)
           
            # Compute acceleration based on the forward vector
            ax = (self.max_acc * thrust) * math.cos(self.theta)
            ay = (self.max_acc * thrust) * math.sin(self.theta)

            # Update velocity
            self.vx += ax 
            self.vy -= ay   

            # Fuel consumption model - 
            v = (self.vx**2 + self.vy**2)**0.5
            efficiency_penalty = self.eff_factor * ((v - self.v_opt)**2/self.v_opt**2)
            spin_cost = abs(spin) * self.fuel_spin_rate
            self.fuel_cost = self.fuel_burn_rate * thrust * (1 + efficiency_penalty) + spin_cost
            self.fuel -= self.fuel_cost
            self.fuel = max(0, self.fuel)  # Prevent negative fuel
        
            
        
        # Apply linear friction
        self.vx *= (1 - self.friction)
        self.vy *= (1 - self.friction)
        
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed < 0.2:  # Threshold to stop the ship
            self.vx = 0
            self.vy = 0

        # Update position
        self.centerx += self.vx 
        self.centery += self.vy 

        # Keep inside screen bounds
        self.centerx = max(self.radius, min(WIDTH - self.radius, self.centerx))
        self.centery = max(self.radius, min(HEIGHT - self.radius, self.centery))

        self.rect.centerx = round(self.centerx)
        self.rect.centery = round(self.centery)

        # Rotate the image to match the current theta
        rotated_image = pygame.transform.rotate(self.original_image, math.degrees(self.theta))
        self.image = rotated_image
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self,thrust, spin):
        self.move(thrust, spin)

    def restart(self):
        self.theta = 0  
        self.vx = 0
        self.vy = 0
        self.omega = 0  # Angular velocity
        self.fuel = self.max_fuel  # Reset fuel
        self.centerx, self.centery = self.start_pos
        self.rect.center = self.start_pos