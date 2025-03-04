import pygame
from Environment import SpaceShipRide
from Human_Agent import Human_Agent

env = SpaceShipRide()
agent = Human_Agent()
# agent = REINFORCE_Agent(1)
env.play(agent)
pygame.quit()
