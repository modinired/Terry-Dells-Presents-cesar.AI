import pygame
from .spritesheet import SpriteSheet

class Enemy(pygame.sprite.Sprite):
    """
    Represents a basic enemy in the game.
    """

    def __init__(self, width, height, sprite_sheet_path="assets/images/enemy_spritesheet.png"):
        """
        Initializes the enemy sprite.
        """
        super().__init__()

        self.walking_frames_l = []
        self.walking_frames_r = []

        sprite_sheet = SpriteSheet(sprite_sheet_path)

        image = sprite_sheet.get_image(0, 0, width, height)
        if image: self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(width, 0, width, height)
        if image: self.walking_frames_r.append(image)

        if not self.walking_frames_r:
            fallback_image = pygame.Surface([width, height])
            fallback_image.fill((128, 0, 128))
            self.walking_frames_r.append(fallback_image)

        for frame in self.walking_frames_r:
            image = pygame.transform.flip(frame, True, False)
            self.walking_frames_l.append(image)

        self.image = self.walking_frames_r[0]
        self.rect = self.image.get_rect()

        self.change_x = 2
        self.boundary_left = 0
        self.boundary_right = 0
        self.level = None

        # --- Animation Timing ---
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 150 # Slower frame rate for the enemy

    def update(self):
        """
        Update the enemy's position and animation.
        """
        self._animate()
        self.rect.x += self.change_x

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