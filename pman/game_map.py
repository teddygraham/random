# game_map.py

import pygame
from settings import TILE_SIZE, BLUE, WHITE

# Define the maze structure (0: wall, 1: path, 3: pellet)
# Modified to make the inaccessible section reachable
original_maze = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 3, 3, 3, 1, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0],
    [1, 3, 0, 3, 3, 3, 3, 3, 0, 3, 1],
    [0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],  # Modified this row to open access
    [0, 1, 3, 3, 0, 1, 3, 0, 3, 3, 0],
    [0, 0, 0, 3, 0, 3, 0, 0, 0, 0, 0],
    [1, 3, 3, 3, 0, 3, 3, 3, 3, 3, 1],
    [0, 3, 0, 1, 3, 3, 0, 0, 1, 0, 0],
    [0, 3, 0, 0, 0, 3, 0, 0, 1, 3, 0],
    [0, 1, 1, 1, 3, 3, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

def reset_maze():
    return [row[:] for row in original_maze]  # Make a fresh copy of the maze

# Function to draw the maze
def draw_maze(screen, maze):
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            if maze[row][col] == 0:  # Wall
                pygame.draw.rect(screen, BLUE, [col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE])
            elif maze[row][col] == 3:  # Pellet
                pygame.draw.circle(screen, WHITE, (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2), 5)
