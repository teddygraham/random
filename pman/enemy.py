# enemy.py

import pygame
import random
from settings import TILE_SIZE, RED

# Class for the Enemy
class Enemy:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
    
    def move(self, maze):
        possible_moves = []
        if maze[(self.y - 1) % len(maze)][self.x] != 0:  # Up
            possible_moves.append([-1, 0])
        if maze[(self.y + 1) % len(maze)][self.x] != 0:  # Down
            possible_moves.append([1, 0])
        if maze[self.y][(self.x - 1) % len(maze[0])] != 0:  # Left
            possible_moves.append([0, -1])
        if maze[self.y][(self.x + 1) % len(maze[0])] != 0:  # Right
            possible_moves.append([0, 1])
        
        if possible_moves:
            move = random.choice(possible_moves)
            self.y = (self.y + move[0]) % len(maze)  # Wrap-around vertically
            self.x = (self.x + move[1]) % len(maze[0])  # Wrap-around horizontally
    
    def draw(self, screen):
        pygame.draw.circle(screen, RED, (self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2), 15)
