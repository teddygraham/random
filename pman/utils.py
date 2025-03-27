# utils.py

import pygame
import time
import sys

# Function to handle the welcome screen and get the player's name
def welcome_screen(screen, font, WINDOW_WIDTH, WINDOW_HEIGHT):
    global player_name
    input_active = True
    player_name = ""
    while input_active:
        screen.fill((0, 0, 0))
        welcome_text = font.render("Welcome", True, (255, 255, 255))
        prompt_text = font.render("Please enter your name:", True, (255, 255, 255))
        name_text = font.render(player_name, True, (255, 255, 255))
        screen.blit(welcome_text, (WINDOW_WIDTH // 2 - welcome_text.get_width() // 2, WINDOW_HEIGHT // 2 - 100))
        screen.blit(prompt_text, (WINDOW_WIDTH // 2 - prompt_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        screen.blit(name_text, (WINDOW_WIDTH // 2 - name_text.get_width() // 2, WINDOW_HEIGHT // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    return player_name  # Return the player's name
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode

# Function to show messages (e.g., Game Over, You Lost, etc.)
def show_message(screen, title, message, font):
    screen.fill((0, 0, 0))
    title_text = font.render(title, True, (255, 255, 255))
    message_text = font.render(message, True, (255, 255, 255))
    screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, screen.get_height() // 2 - 40))
    screen.blit(message_text, (screen.get_width() // 2 - message_text.get_width() // 2, screen.get_height() // 2))
    pygame.display.flip()

# Function to handle player decision to continue or quit
def handle_continue_or_quit():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True  # Continue
                elif event.key == pygame.K_n:
                    return False  # Quit

# Function to display the timer and score
def draw_timer_and_score(screen, start_time, time_limit, collected_pellets, total_pellets, lives, font):
    elapsed_time = time.time() - start_time
    remaining_time = max(0, time_limit - int(elapsed_time))
    timer_text = font.render(f"Time: {remaining_time}s", True, (255, 255, 255))
    score_text = font.render(f"Pellets: {collected_pellets}/{total_pellets}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    screen.blit(timer_text, (10, 10))
    screen.blit(score_text, (10, 50))
    screen.blit(lives_text, (10, 90))
    return remaining_time
