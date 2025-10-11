import pygame
import sys
from .game.player import Player
from .game.level import Level_01

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def draw_ui(screen, score, lives):
    """ Renders the UI elements on the screen. """
    font = pygame.font.SysFont(None, 25)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, [10, 10])
    screen.blit(lives_text, [10, 35])

def game_over_screen(screen):
    """ Displays the game over screen. """
    font = pygame.font.SysFont(None, 50)
    text = font.render("Game Over", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(text, text_rect)

def main():
    """ Main program function. """
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Lavacakes: Pizza Fury")

    # --- Game State ---
    score = 0
    lives = 3
    game_over = False

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
    for enemy in current_level.enemy_list:
        active_sprite_list.add(enemy)

    clock = pygame.time.Clock()

    # --- Main Game Loop ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_LEFT:
                        player.go_left()
                    if event.key == pygame.K_RIGHT:
                        player.go_right()
                    if event.key == pygame.K_SPACE:
                        player.jump()

            if event.type == pygame.KEYUP:
                if not game_over:
                    if event.key == pygame.K_LEFT and player.change_x < 0:
                        player.stop()
                    if event.key == pygame.K_RIGHT and player.change_x > 0:
                        player.stop()

        if not game_over:
            active_sprite_list.update()
            current_level.update()

            # --- Player-Enemy Collision ---
            enemy_hit_list = pygame.sprite.spritecollide(player, current_level.enemy_list, False)

            for enemy in enemy_hit_list:
                if player.change_y > 0:
                    current_level.enemy_list.remove(enemy)
                    active_sprite_list.remove(enemy)
                    score += 100
                else:
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                    else:
                        # Reset level
                        world_shift = current_level.world_shift
                        current_level.shift_world(-world_shift)
                        player.rect.x = 340
                        player.rect.y = SCREEN_HEIGHT - player.rect.height

                        # We need to recreate the level to restore enemies
                        level_list[current_level_no] = Level_01(player)
                        current_level = level_list[current_level_no]
                        player.level = current_level

                        # Reset active sprite list
                        active_sprite_list.empty()
                        active_sprite_list.add(player)
                        for new_enemy in current_level.enemy_list:
                            active_sprite_list.add(new_enemy)


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
        draw_ui(screen, score, lives)

        if game_over:
            game_over_screen(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()