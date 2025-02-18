import pygame
from Graphics import *

class Star (pygame.sprite.Sprite):
    def __init__(self, img, pos = (300,300), scale = (60,60), radius = 20) -> None:
        super().__init__()
        self.image = img
        self.image = pygame.transform.scale(self.image, scale)
        self.rect = self.image.get_rect(center = pos)
        self.radius = radius
        self.mask = pygame.mask.from_surface(self.image)
                
    def draw (self, surface):
        surface.blit(self.image, self.rect)

    def move (self):
        x, y = self.rect.center
        x = (x + 2) % WIDTH
        y = (y + 1) % HEIGHT
        self.rect.center = x, y
    
    def update(self):
        self.move()
        

        