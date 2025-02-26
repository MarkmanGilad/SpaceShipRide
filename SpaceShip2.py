import pygame
import math

# Global constants
WIDTH, HEIGHT = 800, 600
FPS = 60
LIGHTGRAY = (200, 200, 200)

class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, image, pos=(700, 500)) -> None:
        super().__init__()
        self.original_image = image  # Unrotated copy for proper rotation
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.radius = 15
        self.mask = pygame.mask.from_surface(self.image)
        self.start_pos = pos

        # Position and rotation
        self.centerx, self.centery = self.start_pos
        self.theta = 0  
        
        # Velocity and angular velocity
        self.vx = 0
        self.vy = 0
        self.omega = 0  # Angular velocity
        
        # Limits
        self.max_thrust = 150
        self.max_spin = 3

        # Friction parameters
        self.linear_friction = 0.02  # Slows down velocity
        self.angular_friction = 0.05  # Slows down spin

        # Fuel system
        self.max_fuel = 100
        self.fuel = self.max_fuel
        self.fuel_burn_rate = 0.2  # Base fuel consumption per action
        self.efficiency_factor = 0.5  # Increases at full power

    def move(self, dt, F_thrust, T_spin):
        if self.fuel > 0:
            # Update angular velocity and apply friction
            self.omega += self.max_spin * T_spin * dt
            self.omega *= (1 - self.angular_friction)  # Angular friction
            self.theta += self.omega * dt

            # Keep theta in [0, 2*pi)
            self.theta %= (2 * math.pi)

            # Throttle is in [0,1] and only forward
            F_thrust = max(0, min(1, F_thrust))

            # Compute acceleration based on the forward vector
            ax = - (self.max_thrust * F_thrust) * math.sin(self.theta)
            ay = - (self.max_thrust * F_thrust) * math.cos(self.theta)

            # Update velocity
            self.vx += ax * dt
            self.vy += ay * dt

            # Apply linear friction
            self.vx *= (1 - self.linear_friction)
            self.vy *= (1 - self.linear_friction)

            # Fuel consumption model
            fuel_cost = self.fuel_burn_rate * (1 + self.efficiency_factor * (F_thrust ** 2))
            self.fuel -= fuel_cost * dt
            self.fuel = max(0, self.fuel)  # Prevent negative fuel

        # Update position
        self.centerx += self.vx * dt
        self.centery += self.vy * dt

        # Keep inside screen bounds
        self.centerx = max(self.radius, min(WIDTH - self.radius, self.centerx))
        self.centery = max(self.radius, min(HEIGHT - self.radius, self.centery))

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
        self.fuel = self.max_fuel  # Reset fuel
        self.centerx, self.centery = self.start_pos
        self.rect.center = self.start_pos
