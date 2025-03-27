# objects.py

import pygame
from settings import TILE_SIZE, WHITE

class Pellet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
    
    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, WHITE, (self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2), 5)
    
    def collect(self, player_x, player_y):
        if self.x == player_x and self.y == player_y and not self.collected:
            self.collected = True
            return True
        return False
