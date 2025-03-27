# player.py

import pygame
from settings import TILE_SIZE, YELLOW

# Class for the Player
class Player:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.speed = 1
    
    def move(self, dx, dy, maze):
        new_x = (self.x + dx) % len(maze[0])  # Wrap-around horizontally
        new_y = (self.y + dy) % len(maze)     # Wrap-around vertically
        
        if maze[new_y][new_x] != 0:  # Ensure player doesn't move into a wall
            self.x = new_x
            self.y = new_y
    
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2), 15)
