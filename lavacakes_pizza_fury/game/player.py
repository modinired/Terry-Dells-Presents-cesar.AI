import pygame
from .spritesheet import SpriteSheet

# --- Player Constants ---
GRAVITY = 0.35
JUMP_STRENGTH = -10
ACCELERATION = 0.5
FRICTION = -0.12

class BellyHitbox(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__(); self.image = pygame.Surface([40, 20]); self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect(center=center)
        self.lifetime = 100; self.creation_time = pygame.time.get_ticks()
    def update(self):
        if pygame.time.get_ticks() - self.creation_time > self.lifetime: self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_sheet_path=None):
        super().__init__()
        self._load_sprites(sprite_sheet_path)
        self.image = self.idle_frames_r[0]
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.level = None
        self.hitbox_group = pygame.sprite.Group()
        self.on_ground = False
        self.frame = 0; self.last_update = pygame.time.get_ticks(); self.frame_rate = 100
        self.direction = "R"; self.state = "idle"
        self.input_direction = "STOP"

    def _load_sprites(self, sprite_sheet_path):
        self.walking_frames_l, self.walking_frames_r, self.idle_frames_l, self.idle_frames_r = [], [], [], []
        sprite_sheet = SpriteSheet(sprite_sheet_path)
        if not self.walking_frames_r: self.walking_frames_r.append(pygame.Surface([40,60])); self.walking_frames_r[0].fill((0,0,255))
        if not self.walking_frames_l: self.walking_frames_l.append(pygame.Surface([40,60])); self.walking_frames_l[0].fill((0,0,255))
        if not self.idle_frames_r: self.idle_frames_r.append(self.walking_frames_r[0])
        if not self.idle_frames_l: self.idle_frames_l.append(self.walking_frames_l[0])
        self.jump_frame_r = self.walking_frames_r[0]
        self.jump_frame_l = self.walking_frames_l[0]

    def update(self):
        # --- Physics ---
        self.acc = pygame.math.Vector2(0, GRAVITY) # Gravity is always applied
        if self.input_direction == "L": self.acc.x = -ACCELERATION
        if self.input_direction == "R": self.acc.x = ACCELERATION

        self.acc.x += self.vel.x * FRICTION
        self.vel.x += self.acc.x
        if abs(self.vel.x) < 0.1: self.vel.x = 0

        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.rect.centerx = round(self.pos.x)
        self._check_collisions('horizontal')

        self.vel.y += self.acc.y
        self.pos.y += self.vel.y + 0.5 * self.vel.y
        self.rect.bottom = round(self.pos.y)
        self._check_collisions('vertical')

        self.hitbox_group.update()
        self._set_state()
        self._animate()

    def _check_collisions(self, direction):
        if direction == 'horizontal':
            for block in pygame.sprite.spritecollide(self, self.level.platform_list, False):
                if self.vel.x > 0: self.rect.right = block.rect.left
                if self.vel.x < 0: self.rect.left = block.rect.right
                self.pos.x = self.rect.centerx; self.vel.x = 0

        if direction == 'vertical':
            hits = pygame.sprite.spritecollide(self, self.level.platform_list, False)
            self.on_ground = False
            if hits:
                if self.vel.y > 0:
                    self.rect.bottom = hits[0].rect.top
                    self.on_ground = True
                    self.vel.y = 0
                    self.pos.y = self.rect.bottom

    def _set_state(self):
        if not self.on_ground: self.state = "jumping"
        elif abs(self.vel.x) > 0: self.state = "walking"
        else: self.state = "idle"

    def _animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            if self.state == "walking": self.frame = (self.frame + 1) % len(self.walking_frames_l)
            else: self.frame = 0

            if self.direction == "R":
                if self.state == "jumping": self.image = self.jump_frame_r
                elif self.state == "walking": self.image = self.walking_frames_r[self.frame]
                else: self.image = self.idle_frames_r[0]
            else:
                if self.state == "jumping": self.image = self.jump_frame_l
                elif self.state == "walking": self.image = self.walking_frames_l[self.frame]
                else: self.image = self.idle_frames_l[0]

    def jump(self):
        if self.on_ground: self.vel.y = JUMP_STRENGTH

    def attack(self):
        center = (self.rect.centerx + 30, self.rect.centery) if self.direction == "R" else (self.rect.centerx - 30, self.rect.centery)
        self.hitbox_group.add(BellyHitbox(center))

    def go_left(self):
        self.input_direction = "L"
        self.direction = "L"

    def go_right(self):
        self.input_direction = "R"
        self.direction = "R"

    def stop(self):
        self.input_direction = "STOP"