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
    def __init__(self, x, y):
        super().__init__()
        self._create_placeholder_sprites()
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

    def _create_placeholder_sprites(self):
        """ Creates simple, colored sprites for the player. """
        self.walking_frames_l, self.walking_frames_r = [], []
        self.idle_frames_l, self.idle_frames_r = [], []

        frame_1 = pygame.Surface([40, 60]); frame_1.fill((0, 0, 255))
        frame_2 = pygame.Surface([40, 60]); frame_2.fill((0, 100, 255))
        self.walking_frames_r.extend([frame_1, frame_2])

        idle_frame = pygame.Surface([40, 60]); idle_frame.fill((0, 0, 200))
        self.idle_frames_r.append(idle_frame)

        self.jump_frame_r = pygame.Surface([40, 60]); self.jump_frame_r.fill((0, 150, 255))

        for frame in self.walking_frames_r: self.walking_frames_l.append(pygame.transform.flip(frame, True, False))
        for frame in self.idle_frames_r: self.idle_frames_l.append(pygame.transform.flip(frame, True, False))
        self.jump_frame_l = pygame.transform.flip(self.jump_frame_r, True, False)

    def update(self):
        """ Update player state based on physics and input. """
        self.acc = pygame.math.Vector2(0, GRAVITY)

        # --- Horizontal Movement ---
        self.acc.x += self.vel.x * FRICTION
        self.vel.x += self.acc.x
        if abs(self.vel.x) < 0.1: self.vel.x = 0

        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.rect.centerx = round(self.pos.x)
        self._check_collisions('horizontal')

        # --- Vertical Movement ---
        self.vel.y += self.acc.y
        self.pos.y += self.vel.y
        self.rect.bottom = round(self.pos.y)
        self._check_collisions('vertical')

        # --- Final Updates ---
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
        self.acc.x = -ACCELERATION
        self.direction = "L"

    def go_right(self):
        self.acc.x = ACCELERATION
        self.direction = "R"

    def stop(self):
        self.acc.x = 0