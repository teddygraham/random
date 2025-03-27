# main_game.py

import pygame
import sys
import time
import json
from datetime import datetime
from settings import WINDOW_SIZE, PLAYER_LIVES, TIME_LIMIT
from game_map import draw_maze, reset_maze
from player import Player
from enemy import Enemy
from utils import show_message, draw_timer_and_score, welcome_screen, handle_continue_or_quit  # Import utility functions
from game_mechanics import check_collision_with_enemies, handle_pellet_collection, handle_player_movement  # Import game mechanics

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('Pac-Man Modular Game')

# Unpack WINDOW_SIZE into WINDOW_WIDTH and WINDOW_HEIGHT
WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_SIZE

# Define the font
font = pygame.font.Font(None, 36)

# Player and enemy initialization
player = Player(1, 1)
enemies = [Enemy(5, 5), Enemy(7, 7), Enemy(3, 9)]

# Game state variables
lives = PLAYER_LIVES
maze = reset_maze()
collected_pellets = 0
total_pellets = sum(row.count(3) for row in maze)  # Count pellets
start_time = time.time()

# Global variable for player name
player_name = ""

# Leaderboard file
LEADERBOARD_FILE = 'leaderboard.json'

# Function to reset the game state (reset pellets only when a new game starts)
def reset_game(reset_pellets=True):
    global maze, collected_pellets, start_time
    if reset_pellets:
        maze = reset_maze()  # Reset the maze with all pellets
        collected_pellets = 0  # Reset pellet count
    player.x, player.y = 1, 1  # Reset player position
    start_time = time.time()

# Main game loop
def game_loop():
    global collected_pellets, lives
    running = True
    reset_game(reset_pellets=False)  # Don't reset pellets between lives

    while running:
        screen.fill((0, 0, 0))
        draw_maze(screen, maze)  # Draw the maze
        player.draw(screen)  # Draw the player

        # Move the enemies
        for enemy in enemies:
            enemy.move(maze)
            enemy.draw(screen)

        # Check for pellet collection
        if handle_pellet_collection(player, maze):
            collected_pellets += 1

        # Check for player collision with enemies
        if check_collision_with_enemies(player, enemies):
            lives -= 1
            if lives > 0:
                show_message(screen, "You Lost", "Play next life? (Y/N)", font)
                if handle_continue_or_quit():
                    reset_game(reset_pellets=False)  # Keep the current pellet count
                else:
                    running = False
            else:
                show_message(screen, "Game Over", "Play again? (Y/N)", font)
                if handle_continue_or_quit():
                    lives = PLAYER_LIVES
                    reset_game(reset_pellets=True)  # Reset pellets for new game
                else:
                    running = False

        # Draw timer and score
        remaining_time = draw_timer_and_score(screen, start_time, TIME_LIMIT, collected_pellets, total_pellets, lives, font)

        # Check if the player won by collecting all pellets before the time runs out
        if collected_pellets == total_pellets:
            time_left = TIME_LIMIT - int(time.time() - start_time)
            show_message(screen, "You won!", f"Time Left: {time_left}s", font)
            update_leaderboard(player_name, lives, time_left)  # Save the player, lives, and time
            display_leaderboard()  # Display the leaderboard
            running = False  # Exit the game loop to avoid replaying immediately

        # Handle player movement and quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Exit the game loop when the exit button is pressed

        # Handle arrow key input for player movement
        keys = pygame.key.get_pressed()
        handle_player_movement(keys, player, maze)

        pygame.display.flip()
        pygame.time.Clock().tick(10)

    pygame.quit()  # Ensure the game quits properly when the loop exits
    sys.exit()  # Close the game window

# Run the welcome screen first
player_name = welcome_screen(screen, font, WINDOW_WIDTH, WINDOW_HEIGHT)

# Start the game loop
game_loop()
