import pygame
from .enemy import Enemy
from .spritesheet import SpriteSheet

class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, image_path=None):
        super().__init__()
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
            except pygame.error:
                self.image = pygame.Surface([width, height]); self.image.fill((0, 255, 0))
        else:
            self.image = pygame.Surface([width, height]); self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()

class Goal(Platform):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.image.fill((255, 215, 0))

class Level():
    def __init__(self, player, background_paths=None):
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.goal = pygame.sprite.GroupSingle()
        self.player = player
        self.world_shift = 0

        self.backgrounds = []
        if background_paths:
            for path in background_paths:
                try:
                    self.backgrounds.append(pygame.image.load(path).convert_alpha())
                except pygame.error: pass

    def update(self):
        self.platform_list.update()
        self.enemy_list.update()
        self.goal.update()

    def draw(self, screen):
        screen.fill((0,0,0))
        if self.backgrounds:
            for i, bg in enumerate(self.backgrounds):
                # Slower layers in the back, faster in the front
                speed = (i + 1) * 0.25
                background_x = (self.world_shift * speed) % bg.get_width()
                screen.blit(bg, (background_x - bg.get_width(), 0))
                if background_x < screen.get_width():
                    screen.blit(bg, (background_x, 0))

        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.goal.draw(screen)

    def shift_world(self, shift_x):
        self.world_shift += shift_x
        for platform in self.platform_list: platform.rect.x += shift_x
        for enemy in self.enemy_list: enemy.rect.x += shift_x
        if self.goal.sprite: self.goal.sprite.rect.x += shift_x


class Level_01(Level):
    def __init__(self, player, background_paths=["assets/images/backgrounds/sky.png", "assets/images/backgrounds/buildings.png"]):
        Level.__init__(self, player, background_paths)
        self.level_limit = -1500

        level_platforms = [ [2000, 70, 0, 580, "assets/images/platforms/street.png"] ]
        for data in level_platforms:
            block = Platform(data[0], data[1], data[4] if background_paths else None)
            block.rect.x = data[2]; block.rect.y = data[3]
            self.platform_list.add(block)

        if background_paths:
            enemy = Enemy(30, 50); enemy.rect.x = 800; enemy.rect.y = 530
            enemy.boundary_left = 800; enemy.boundary_right = 1010
            self.enemy_list.add(enemy)

        goal = Goal(50, 50); goal.rect.x = 1800; goal.rect.y = 530
        self.goal.add(goal)

class Level_02(Level):
    def __init__(self, player, background_paths=["assets/images/backgrounds/sky.png", "assets/images/backgrounds/buildings.png"]):
        Level.__init__(self, player, background_paths)
        self.level_limit = -1000

        level_platforms = [ [210, 30, 450, 570, "assets/images/platforms/street.png"] ]
        for data in level_platforms:
            block = Platform(data[0], data[1], data[4] if background_paths else None)
            block.rect.x = data[2]; block.rect.y = data[3]
            self.platform_list.add(block)

        goal = Goal(50, 50); goal.rect.x = 1200; goal.rect.y = 530
        self.goal.add(goal)