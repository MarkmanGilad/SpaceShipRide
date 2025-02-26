import pygame
from Graphics import *
from SpaceShip2 import SpaceShip
from Star import Star
import random
import torch
from Human_Agent import Human_Agent
from REINFORCE_Agent import REINFORCE_Agent

class SpaceShipRide:
    def __init__(self):
        self.init_rewards()
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT+H_HEIGHT))
        self.header_surf = pygame.Surface((WIDTH, H_HEIGHT))
        self.main_surf = pygame.Surface((WIDTH, HEIGHT))
        
        self.color = LIGHTGRAY
        self.clear()
        self.blit()

        pygame.display.set_caption('Space Ride')
        self.clock = pygame.time.Clock()

        # Load and scale spaceship image
        space_ship_img = pygame.image.load("img/spacecraft.png")
        space_ship_img = pygame.transform.scale(space_ship_img, (30, 30))
        self.space_ship = SpaceShip(space_ship_img, pos=(700,550))

        # sun_img = pygame.image.load("img/sun.png")
        # self.sun = Star(sun_img, pos=(700,100), radius=20)

        dead_star_img = pygame.image.load("img/starwars.png")
        self.dead_star = Star(dead_star_img, pos=(100,100), scale=(20,20), radius=10)
        
        
        self.run = True
        self.reward = 0
        self.step = 0
        self.max_step = 1000
        
        # self.dis_sun = self.calc_dist_sun()
        self.dis_dead_star = self.calc_dist_dead_star()

    def init_rewards(self):
        self.losse = -10
        self.win = 10
        self.poitive_reward = 0.5
        self.negative_reward = -0.1
        self.time_reward = -0.01

    def render (self, action):
        F_thrust, T_spin = action
        # dt = self.clock.tick(FPS) / 1000  # returns milliseconds since last call
        dt = 1/60
        self.clear()
        self.space_ship.update(dt, F_thrust, T_spin)
        self.space_ship.draw(self.main_surf)
        # self.sun.draw(self.main_surf)  
        self.dead_star.draw(self.main_surf)
        

        if self.step > self.max_step:
            # self.color = pygame.Color('Red')
            self.done = True
            self.reward = self.losse
        # elif pygame.sprite.collide_circle(self.space_ship, self.sun):
        #     # self.color = pygame.Color('LightGreen')
        #     self.done = True
        #     self.reward = self.win
            
        elif pygame.sprite.collide_circle(self.space_ship, self.dead_star):
            # self.color = pygame.Color('Red')
            self.done = True
            self.reward = self.losse
        else:
            self.color = LIGHTGRAY
        
        # self.write(f"time: {self.max_step-self.step} reward: {self.get_reward()}")
        self.blit()
        pygame.display.update()

        # Wrap-around logic
        if self.space_ship.rect.centerx < 0 or self.space_ship.rect.centerx > WIDTH or \
                self.space_ship.rect.centery < 0 or self.space_ship.rect.centery > HEIGHT:
            self.done = True
            self.reward = self.losse
        

    def play (self, agent):
        self.max_step = 1000
        self.run = True
        self.done = False
        self.step = 0
        while self.run:
            self.step += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            # pygame.event.pump()
                        
            action = agent.get_action(self.get_state()) 
            print(" "* 100, end="\r")
            print (f"step: {self.step} reward: {self.get_reward()} ", end = "\r")
            self.render(action)
            if self.done:
                print (f"\nstep: {self.step} reward: {self.get_reward()} ")
                self.restart()
            self.clock.tick(FPS)
    

    def get_state(self):
        norm = 500
        state = []
        #spaceship pos, vx, vy, theta, omega, radius, step to end
        state.append(self.space_ship.rect.centerx/norm)
        state.append(self.space_ship.rect.centery/norm)
        state.append(self.space_ship.vx/norm)
        state.append(self.space_ship.vy/norm)
        state.append(self.space_ship.theta)
        state.append(self.space_ship.omega)
        state.append(self.space_ship.radius/norm)
        state.append(self.max_step - self.step/200)
        #sun distance, radius
        # state.append((self.sun.rect.centerx - self.space_ship.rect.centerx)/norm)
        # state.append((self.sun.rect.centery - self.space_ship.rect.centery)/norm)
        # state.append(self.sun.radius/norm)
        #death star distance, radius
        state.append((self.dead_star.rect.centerx - self.space_ship.rect.centerx)/norm)
        state.append((self.dead_star.rect.centery - self.space_ship.rect.centery)/norm)
        state.append(self.dead_star.radius/norm)

        return torch.tensor(state, dtype=torch.float32)

    def get_reward(self):
        if self.done:
            return self.reward
        # dis_sun = self.dis_sun - self.calc_dist_sun()
        # self.dis_sun = self.calc_dist_sun()
        dis_dead_star = self.dis_dead_star - self.calc_dist_dead_star()
        self.dis_dead_star = self.calc_dist_dead_star()
        # return dis_sun * self.poitive_reward + dis_dead_star*self.negative_reward + self.time_reward
        return dis_dead_star*self.negative_reward + self.time_reward
    
    def restart (self):
        self.done = False
        self.step = 0
        self.reward = 0
        self.space_ship.restart()
        # self.dis_sun = self.calc_dist_sun()
        self.dis_dead_star = self.calc_dist_dead_star()

    def calc_dist_sun (self):
        return abs(self.sun.rect.centerx - self.space_ship.rect.centerx) + abs(self.sun.rect.centery - self.space_ship.rect.centery)
        
    def calc_dist_dead_star(self):
        return abs(self.dead_star.rect.centerx - self.space_ship.rect.centerx) + abs(self.dead_star.rect.centery - self.space_ship.rect.centery)
        
    def write(self, txt, pos=(10,10)):
        font = pygame.font.SysFont("Arial", 36)
        txt_surf = font.render(txt, True, WHITE)
        self.header_surf.blit(txt_surf, pos)

    def clear(self):
        self.header_surf.fill(BLUE)
        self.main_surf.fill(self.color)

    def blit(self):
        self.screen.blit(self.header_surf, (0,0))
        self.screen.blit(self.main_surf, (0,100))

if __name__ == "__main__":
    env = SpaceShipRide()
    agent = Human_Agent()
    # agent = REINFORCE_Agent(1)
    env.play(agent)
    pygame.quit()
