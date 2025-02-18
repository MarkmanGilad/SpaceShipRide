import pygame
from Graphics import *
from SpaceShip import SpaceShip
from Star import Star
import random
import torch
from Human_Agent import Human_Agent

class SpaceShipRide:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Space Ride')
        self.clock = pygame.time.Clock()

        # Load and scale spaceship image
        space_ship_img = pygame.image.load("img/spacecraft.png")
        space_ship_img = pygame.transform.scale(space_ship_img, (60, 60))
        self.space_ship = SpaceShip(space_ship_img)

        sun_img = pygame.image.load("img/sun.png")
        self.sun = Star(sun_img, (100,100), radius=20)

        dead_star_img = pygame.image.load("img/starwars.png")
        self.dead_star = Star(dead_star_img, (400,300), scale=(150,150), radius=70)
        
        self.color = LIGHTGRAY
        self.run = True
        self.reward = 0
        self.step = 0
        self.max_step = 1000
        
        self.dis_sun = self.calc_dist_sun()
        self.dis_dead_star = self.calc_dist_dead_star()

    def render (self, action ):
        F_thrust, T_spin = action
        dt = self.clock.tick(FPS) / 500  # returns milliseconds since last call
        self.screen.fill(self.color)
        self.space_ship.update(dt, F_thrust, T_spin)
        self.space_ship.draw(self.screen)
        self.sun.draw(self.screen)  
        self.dead_star.draw(self.screen)
        

        if self.step > self.max_step:
            self.color = pygame.Color('Red')
            self.done = True
            self.reward = -100
        elif pygame.sprite.collide_circle(self.space_ship, self.sun):
            self.color = pygame.Color('LightGreen')
            self.done = True
            self.reward = 100
            
        elif pygame.sprite.collide_circle(self.space_ship, self.dead_star):
            self.color = pygame.Color('Red')
            self.done = True
            self.reward = -100
        else:
            self.color = LIGHTGRAY

        pygame.display.update()

        # Wrap-around logic
        if self.space_ship.rect.centerx < 0:
            self.space_ship.rect.centerx = WIDTH
            self.done = True
            self.reward = -100
        elif self.space_ship.rect.centerx > WIDTH:
            self.space_ship.rect.centerx = 0
            self.done = True
            self.reward = -100
        if self.space_ship.rect.centery < 0:
            self.space_ship.rect.centery = HEIGHT
            self.done = True
            self.reward = -100
        elif self.space_ship.rect.centery > HEIGHT:
            self.space_ship.rect.centery = 0
            self.done = True
            self.reward = -100

    def play (self):
        agent = Human_Agent()
        self.run = True
        self.done = False
        self.step = 0
        while self.run:
            self.step += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            pygame.event.pump()
                        
            action = agent.get_Action()# (0.1, random.random()-0.5)
            print(" "* 100, end="\r")
            print (f"step: {self.step} reward: {self.get_reward()} ", end = "\r")
            self.render(action)
            if self.done:
                print (f"\nstep: {self.step} reward: {self.get_reward()} ")
                self.restart()

    def get_state(self):
        state = []
        #spaceship pos, vx, vy, theta, omega
        state.append(self.space_ship.rect.centerx)
        state.append(self.space_ship.rect.centery)
        state.append(self.space_ship.vx)
        state.append(self.space_ship.vy)
        state.append(self.space_ship.theta)
        state.append(self.space_ship.omega)
        state.append(self.space_ship.radius)
        #sun distance, radius
        state.append(self.sun.rect.centerx - self.space_ship.rect.centerx)
        state.append(self.sun.rect.centery - self.space_ship.rect.centery)
        state.append(self.sun.radius)
        #death star distance, radius
        state.append(self.dead_star.rect.centerx - self.space_ship.rect.centerx)
        state.append(self.dead_star.rect.centery - self.space_ship.rect.centery)
        state.append(self.dead_star.radius)

        return torch.tensor(state, dtype=torch.float32)

    def get_reward(self):
        if self.done:
            return self.reward
        dis_sun = self.dis_sun - self.calc_dist_sun()
        self.dis_sun = self.calc_dist_sun()
        dis_dead_star = self.dis_dead_star - self.calc_dist_dead_star()
        self.dis_dead_star = self.calc_dist_dead_star()
        return dis_sun * 10 + -dis_dead_star*1
        
    def restart (self):
        self.done = False
        self.step = 0
        self.reward = 0
        self.space_ship.restart()

    def calc_dist_sun (self):
        return abs(self.sun.rect.centerx - self.space_ship.rect.centerx) + abs(self.sun.rect.centery - self.space_ship.rect.centery)
        
    def calc_dist_dead_star(self):
        return abs(self.dead_star.rect.centerx - self.space_ship.rect.centerx) + abs(self.dead_star.rect.centery - self.space_ship.rect.centery)
        

if __name__ == "__main__":
    env = SpaceShipRide()
    env.play()
    pygame.quit()
