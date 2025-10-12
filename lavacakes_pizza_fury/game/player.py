import pygame
from .spritesheet import SpriteSheet

class Player(pygame.sprite.Sprite):
    """
    Represents the player character in Lavacakes: Pizza Fury.
    """
    def __init__(self, x, y, sprite_sheet_path="assets/images/player_spritesheet.png"):
        """
        Initializes the player sprite.
        """
        super().__init__()

        self.walking_frames_l = []
        self.walking_frames_r = []
        self.idle_frames_l = []
        self.idle_frames_r = []
        self.jump_frame_l = None
        self.jump_frame_r = None
        self.direction = "R"
        self.state = "idle"

        sprite_sheet = SpriteSheet(sprite_sheet_path)

        # Load animation frames
        image = sprite_sheet.get_image(0, 0, 66, 90)
        if image: self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(66, 0, 66, 90)
        if image: self.walking_frames_r.append(image)

        image = sprite_sheet.get_image(0, 90, 66, 90)
        if image: self.idle_frames_r.append(image)

        self.jump_frame_r = sprite_sheet.get_image(66, 90, 66, 90)

        # Create left-facing frames
        for frame in self.walking_frames_r: self.walking_frames_l.append(pygame.transform.flip(frame, True, False))
        for frame in self.idle_frames_r: self.idle_frames_l.append(pygame.transform.flip(frame, True, False))
        if self.jump_frame_r: self.jump_frame_l = pygame.transform.flip(self.jump_frame_r, True, False)

        # Create fallback images if no frames were loaded
        if not self.walking_frames_r: self.walking_frames_r.append(pygame.Surface([40,60])); self.walking_frames_r[0].fill((0,0,255))
        if not self.walking_frames_l: self.walking_frames_l.append(pygame.Surface([40,60])); self.walking_frames_l[0].fill((0,0,255))
        if not self.idle_frames_r: self.idle_frames_r.append(self.walking_frames_r[0])
        if not self.idle_frames_l: self.idle_frames_l.append(self.walking_frames_l[0])
        if not self.jump_frame_r: self.jump_frame_r = self.walking_frames_r[0]
        if not self.jump_frame_l: self.jump_frame_l = self.walking_frames_l[0]

        self.image = self.idle_frames_r[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.change_x = 0
        self.change_y = 0
        self.level = None

        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100

    def update(self):
        self.calc_grav()
        self._set_state()
        self._animate()

        self.rect.x += self.change_x
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_x > 0: self.rect.right = block.rect.left
            elif self.change_x < 0: self.rect.left = block.rect.right

        self.rect.y += self.change_y
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_y > 0: self.rect.bottom = block.rect.top
            elif self.change_y < 0: self.rect.top = block.rect.bottom
            self.change_y = 0

    def _set_state(self):
        if self.change_y != 0: self.state = "jumping"
        elif self.change_x != 0: self.state = "walking"
        else: self.state = "idle"

    def _animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now

            if self.state == "walking":
                self.frame = (self.frame + 1) % len(self.walking_frames_l)
                if self.direction == "R": self.image = self.walking_frames_r[self.frame]
                else: self.image = self.walking_frames_l[self.frame]
            elif self.state == "idle":
                self.frame = (self.frame + 1) % len(self.idle_frames_l)
                if self.direction == "R": self.image = self.idle_frames_r[self.frame]
                else: self.image = self.idle_frames_l[self.frame]
            elif self.state == "jumping":
                if self.direction == "R": self.image = self.jump_frame_r
                else: self.image = self.jump_frame_l

    def calc_grav(self):
        if self.change_y == 0: self.change_y = 1
        else: self.change_y += .35

    def jump(self):
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2
        if len(platform_hit_list) > 0 or self.rect.bottom >= 600:
            self.change_y = -10

    def go_left(self):
        self.change_x = -6
        self.direction = "L"

    def go_right(self):
        self.change_x = 6
        self.direction = "R"

    def stop(self):
        self.change_x = 0