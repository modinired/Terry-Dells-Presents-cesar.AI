import pygame
from .spritesheet import SpriteSheet

class Enemy(pygame.sprite.Sprite):
    """ Represents a basic enemy in the game. """

    def __init__(self, width, height):
        """ Initializes the enemy sprite. """
        super().__init__()

        self._create_placeholder_sprites(width, height)
        self.image = self.walking_frames_r[0]
        self.rect = self.image.get_rect()

        self.change_x = 2
        self.boundary_left = 0
        self.boundary_right = 0
        self.level = None

        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 150

    def _create_placeholder_sprites(self, width, height):
        """ Creates simple, colored sprites for the enemy. """
        self.walking_frames_l, self.walking_frames_r = [], []

        frame_1 = pygame.Surface([width, height]); frame_1.fill((128, 0, 128))
        frame_2 = pygame.Surface([width, height]); frame_2.fill((180, 0, 180))
        self.walking_frames_r.extend([frame_1, frame_2])

        for frame in self.walking_frames_r:
            self.walking_frames_l.append(pygame.transform.flip(frame, True, False))

    def update(self):
        """ Update the enemy's position and animation. """
        self.rect.x += self.change_x
        self._animate()

        if self.rect.right > self.boundary_right or self.rect.left < self.boundary_left:
            self.change_x *= -1

    def _animate(self):
        """ Handles the enemy's animation. """
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame = (self.frame + 1) % len(self.walking_frames_l)
            if self.change_x > 0:
                self.image = self.walking_frames_r[self.frame]
            else:
                self.image = self.walking_frames_l[self.frame]