import pygame
import sys
from .game.player import Player
from .game.level import Level_01, Level_02
from .game.sound_manager import SoundManager

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

    sound_manager = SoundManager()
    sound_manager.load_sound('jump', 'assets/sounds/jump.wav')
    sound_manager.load_sound('stomp', 'assets/sounds/stomp.wav')
    sound_manager.load_sound('punch', 'assets/sounds/punch.wav')
    sound_manager.load_sound('death', 'assets/sounds/death.wav')
    sound_manager.load_music('assets/music/background.ogg')
    sound_manager.play_music()

    score = 0
    lives = 3
    game_over = False

    player = Player(50, 50)

    level_list = []
    level_list.append(Level_01(player))
    level_list.append(Level_02(player))

    current_level_no = 0
    current_level = level_list[current_level_no]

    player.level = current_level
    player.pos.x = 340
    player.pos.y = SCREEN_HEIGHT - 100

    active_sprite_list = pygame.sprite.Group()
    active_sprite_list.add(player)
    for enemy in current_level.enemy_list:
        active_sprite_list.add(enemy)

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                        sound_manager.play_sound('jump')
                    if event.key == pygame.K_x:
                        player.attack()
                        sound_manager.play_sound('punch')

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: player.go_left()
            elif keys[pygame.K_RIGHT]: player.go_right()
            else: player.stop()

            active_sprite_list.update()
            current_level.update()

            # --- Belly Punch Collision ---
            belly_hits = pygame.sprite.groupcollide(player.hitbox_group, current_level.enemy_list, True, True)
            if belly_hits:
                score += 150
                sound_manager.play_sound('stomp')

            # --- Stomp/Run-in Collision ---
            enemy_hit_list = pygame.sprite.spritecollide(player, current_level.enemy_list, False)
            for enemy in enemy_hit_list:
                if player.vel.y > 0 and player.rect.bottom < enemy.rect.bottom:
                    current_level.enemy_list.remove(enemy)
                    active_sprite_list.remove(enemy)
                    score += 100
                    sound_manager.play_sound('stomp')
                else:
                    lives -= 1
                    sound_manager.play_sound('death')
                    if lives <= 0: game_over = True
                    else:
                        world_shift = current_level.world_shift
                        current_level.shift_world(-world_shift)
                        player.pos.x = 340
                        player.pos.y = SCREEN_HEIGHT - 100
                        level_list[current_level_no] = type(current_level)(player)
                        current_level = level_list[current_level_no]
                        player.level = current_level
                        active_sprite_list.empty(); active_sprite_list.add(player)
                        for new_enemy in current_level.enemy_list: active_sprite_list.add(new_enemy)

            # --- Level Transition ---
            if pygame.sprite.spritecollide(player, current_level.goal, False):
                current_level_no += 1
                if current_level_no < len(level_list):
                    current_level = level_list[current_level_no]
                    player.level = current_level
                    player.pos.x = 340; player.pos.y = SCREEN_HEIGHT - 100
                    active_sprite_list.empty(); active_sprite_list.add(player)
                    for enemy in current_level.enemy_list: active_sprite_list.add(enemy)
                else:
                    game_over = True

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
            sound_manager.stop_music()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()