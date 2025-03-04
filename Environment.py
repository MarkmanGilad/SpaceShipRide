
import pygame
from Graphics import *
from SpaceShip2 import SpaceShip
import torch
from Human_Agent import Human_Agent
from REINFORCE_Agent import REINFORCE_Agent
from Star import Star

class SpaceShipRide:
    def __init__(self):
        
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
        self.space_ship = SpaceShip(pos=(700,550))

        # sun_img = pygame.image.load("img/sun.png")
        # self.sun = Star(sun_img, pos=(700,100), radius=20)

        dead_star_img = pygame.image.load("img/starwars.png")
        self.dead_star = Star(dead_star_img, pos=(100,100), scale=(40,40), radius=20)
        
        
        self.run = True
        self.reward = 0
        self.step = 0
        self.max_step = 1000
        self.win = False
        
        # self.dis_sun = self.calc_dist_sun()
        self.dis_dead_star = self.calc_dist_dead_star()
        self.init_rewards()

    def init_rewards(self):
        self.losse = -50
        self.win = 200
        self.dist_reward = 1
        self.fuel_reward = -0.1
        self.time_reward = -0.1
        self.space_ship.fuel_cost = 1
        self.space_ship.fuel_burn_rate = 0.5  # Base fuel consumption per action
        self.space_ship.eff_factor = 0.1  # Increases at full power
        self.space_ship.fuel_spin_rate = 10  # Fuel cost multiplier for spin

        
        

    def render (self, action):
        thrust, spin = action
        
        self.clear()
        self.space_ship.update(thrust, spin)
        self.space_ship.draw(self.main_surf)
        self.dead_star.update()
        self.dead_star.draw(self.main_surf)
        

        if self.step > self.max_step:
            self.done = True
            self.reward = self.losse
        elif self.space_ship.fuel == 0:
            self.done = True
            self.reward = self.losse
        elif pygame.sprite.collide_mask(self.space_ship, self.dead_star):
            self.done = True
            self.reward = self.win
            self.win = True
            

        if self.step % 10 == 0:
            self.write(f"time: {self.max_step-self.step}     fuel: {self.space_ship.fuel:.1f}      dist to star {self.calc_dist_dead_star():.1f}")
            self.write(f"reward: {self.get_reward():.2f} ", pos=(10,50))
            self.blit_header()
        self.blit_main()
        pygame.display.update()


    def play (self, agent):
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
        state.append(self.space_ship.radius/norm)
        state.append(self.space_ship.fuel/self.space_ship.max_fuel)
        state.append((self.max_step - self.step)/self.max_step)
        state.append((self.dead_star.rect.centerx - self.space_ship.rect.centerx)/norm)
        state.append((self.dead_star.rect.centery - self.space_ship.rect.centery)/norm)
        state.append(self.dead_star.radius/norm)

        return torch.tensor(state, dtype=torch.float32)

    def get_reward(self):
        if self.done:
            proximity_penalty = 0
            if self.reward == self.losse:  # If the agent loses
                proximity_penalty = self.losse * (self.dis_dead_star / WIDTH)  # Scale by distance
            return self.reward + proximity_penalty  # Still negative, but less harsh when closer
            
                
        delta_dis_dead_star = self.dis_dead_star - self.calc_dist_dead_star()
        self.dis_dead_star = self.calc_dist_dead_star()
        dis_reward = delta_dis_dead_star*self.dist_reward
        reward = dis_reward + self.time_reward + self.space_ship.fuel_cost * self.fuel_reward
        return  reward
    
    def restart (self):
        self.done = False
        self.step = 0
        self.reward = 0
        self.space_ship.restart()
        self.dis_dead_star = self.calc_dist_dead_star()
        self.win = False

    def calc_dist_sun (self):
        return abs(self.sun.rect.centerx - self.space_ship.rect.centerx) + abs(self.sun.rect.centery - self.space_ship.rect.centery)
        
    def calc_dist_dead_star(self):
        return ((self.dead_star.rect.centerx - self.space_ship.rect.centerx)**2 + (self.dead_star.rect.centery - self.space_ship.rect.centery)**2)**0.5
        
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

    def blit_header(self):
        self.screen.blit(self.header_surf, (0,0))

    def blit_main(self):
        self.screen.blit(self.main_surf, (0,100))
        

if __name__ == "__main__":
    env = SpaceShipRide()
    agent = Human_Agent()
    # agent = REINFORCE_Agent(1)
    env.play(agent)
    pygame.quit()


