# game_mechanics.py

import pygame  # Add pygame import

def check_collision_with_enemies(player, enemies):
    """Check if the player collides with any enemies."""
    for enemy in enemies:
        if player.x == enemy.x and player.y == enemy.y:
            return True
    return False

def handle_pellet_collection(player, maze):
    """Handle the logic for collecting pellets."""
    collected = False
    if maze[player.y][player.x] == 3:  # Check if on a pellet
        maze[player.y][player.x] = 1  # Change to path
        collected = True
    return collected

def handle_player_movement(keys, player, maze):
    """Handle the player movement based on key input."""
    if keys[pygame.K_LEFT]:
        player.move(-1, 0, maze)
    if keys[pygame.K_RIGHT]:
        player.move(1, 0, maze)
    if keys[pygame.K_UP]:
        player.move(0, -1, maze)
    if keys[pygame.K_DOWN]:
        player.move(0, 1, maze)
