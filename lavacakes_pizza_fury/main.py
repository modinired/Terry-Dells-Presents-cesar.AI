import pygame
import sys
from game.player import Player
from game.platforms import Platform

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def main():
    """ Main program function. """
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Lavacakes: Pizza Fury")

    # --- Create the sprite lists ---
    all_sprites_list = pygame.sprite.Group()
    platform_list = pygame.sprite.Group()

    # --- Create the platforms ---
    level = [
        (500, 50, 0, 550),      # Ground
        (200, 30, 200, 400),
        (150, 30, 500, 300),
    ]

    for plat in level:
        platform = Platform(plat[0], plat[1])
        platform.rect.x = plat[2]
        platform.rect.y = plat[3]
        platform_list.add(platform)
        all_sprites_list.add(platform)

    # --- Create the player ---
    player = Player(50, 50)
    player.level = platform_list
    all_sprites_list.add(player)

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

        all_sprites_list.update()

        screen.fill(BLACK)
        all_sprites_list.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()