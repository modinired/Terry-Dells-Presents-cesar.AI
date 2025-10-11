import pygame
import sys
from game.player import Player

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def main():
    """ Main program function. """
    # Initialize Pygame
    pygame.init()

    # Create the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Lavacakes: Pizza Fury")

    # --- Sprite Lists ---
    all_sprites_list = pygame.sprite.Group()

    # Create the player
    player = Player(50, 500)
    all_sprites_list.add(player)

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # --- Main Game Loop ---
    running = True
    while running:
        # --- Event Processing ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # --- Keyboard Controls ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        # --- Game Logic ---
        all_sprites_list.update()

        # --- Drawing Code ---
        screen.fill(WHITE)
        all_sprites_list.draw(screen)

        # --- Update the screen ---
        pygame.display.flip()

        # --- Limit to 60 frames per second ---
        clock.tick(60)

    # Quit Pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()