# Animation
import pygame
from Graphics import *
from SpaceShip import SpaceShip
from Star import Star

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Reversi')
clock = pygame.time.Clock()

# Load and scale spaceship image
space_ship_img = pygame.image.load("img/spacecraft.png")
space_ship_img = pygame.transform.scale(space_ship_img, (60, 60))
space_ship = SpaceShip(space_ship_img, (700, 500))

sun_img = pygame.image.load("img/sun.png")
sun = Star(sun_img, (100,100))

dead_star_img = pygame.image.load("img/starwars.png")
dead_star = Star(dead_star_img, (400,300), scale=(150,150))

F_thrust = 0
T_spin = 0
color = LIGHTGRAY
run = True
while run:
    dt = clock.tick(FPS) / 500  # returns milliseconds since last call

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.event.pump()
    # Use key state instead of events for continuous input:
    keys = pygame.key.get_pressed()
    F_thrust = 0
    T_spin = 0
    if keys[pygame.K_UP]:
        F_thrust = 0.5  # Apply continuous forward thrust
    if keys[pygame.K_DOWN]:
        pass
        # F_thrust = -0.5  # Reverse thrust
    if keys[pygame.K_RIGHT]:
        T_spin = -0.5  # Clockwise rotation
    if keys[pygame.K_LEFT]:
        T_spin = 0.5   # Counter-clockwise rotation

    screen.fill(color)
    space_ship.update(dt, F_thrust, T_spin)
    space_ship.draw(screen)
    # sun.move()
    sun.draw(screen)  
    dead_star.draw(screen)

    if pygame.sprite.collide_mask(space_ship, sun):
        color = pygame.Color('LightGreen')
    elif pygame.sprite.collide_mask(space_ship, dead_star):
        color = pygame.Color('Red')
    else:
        color = LIGHTGRAY


    pygame.display.update()


pygame.quit()
