import pygame
import sys
from game.player import Player
from game.level import Level_01

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def main():
    """ Main program function. """
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Lavacakes: Pizza Fury")

    # --- Create the player ---
    player = Player(50, 50)

    # --- Create all the levels ---
    level_list = []
    level_list.append(Level_01(player))

    # Set the current level
    current_level_no = 0
    current_level = level_list[current_level_no]

    player.level = current_level
    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height

    active_sprite_list = pygame.sprite.Group()
    active_sprite_list.add(player)

    clock = pygame.time.Clock()

    # --- Main Game Loop ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_SPACE:
                    player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        active_sprite_list.update()
        current_level.update()

        # --- Scrolling Logic ---
        if player.rect.right >= 500:
            diff = player.rect.right - 500
            player.rect.right = 500
            current_level.shift_world(-diff)

        if player.rect.left <= 120:
            diff = 120 - player.rect.left
            player.rect.left = 120
            current_level.shift_world(diff)

        # --- Drawing Code ---
        current_level.draw(screen)
        active_sprite_list.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()