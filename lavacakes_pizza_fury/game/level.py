import pygame
from .enemy import Enemy
from .spritesheet import SpriteSheet

class Platform(pygame.sprite.Sprite):
    """ Represents a platform in the game world. """
    def __init__(self, width, height, color=(0, 255, 0)):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

class Goal(Platform):
    """ Represents the goal at the end of a level. """
    def __init__(self, width, height):
        super().__init__(width, height, (255, 215, 0))

class Level():
    """ This is a generic super-class used to define a level. """
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.goal = pygame.sprite.GroupSingle()
        self.player = player
        self.world_shift = 0
        self.background_color = (0, 0, 0) # Black

    def update(self):
        """ Update everything on this level. """
        self.platform_list.update()
        self.enemy_list.update()
        self.goal.update()

    def draw(self, screen):
        """ Draw everything on this level. """
        screen.fill(self.background_color)
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.goal.draw(screen)

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll everything. """
        self.world_shift += shift_x
        for platform in self.platform_list: platform.rect.x += shift_x
        for enemy in self.enemy_list: enemy.rect.x += shift_x
        if self.goal.sprite: self.goal.sprite.rect.x += shift_x


class Level_01(Level):
    """ Definition for level 1. """
    def __init__(self, player):
        Level.__init__(self, player)
        self.level_limit = -1500

        # --- To use your own art, replace these placeholder platforms ---
        # --- with calls to the Platform class with image paths. See ASSETS_NEEDED.md ---

        level_platforms = [ [2000, 70, 0, 580], [210, 70, 500, 500], [210, 70, 800, 400] ]
        for platform_data in level_platforms:
            block = Platform(platform_data[0], platform_data[1])
            block.rect.x = platform_data[2]
            block.rect.y = platform_data[3]
            self.platform_list.add(block)

        enemy = Enemy(30, 50)
        enemy.rect.x = 800; enemy.rect.y = 350
        enemy.boundary_left = 800; enemy.boundary_right = 1010
        self.enemy_list.add(enemy)

        goal = Goal(50, 50)
        goal.rect.x = 1800; goal.rect.y = 530
        self.goal.add(goal)


class Level_02(Level):
    """ Definition for level 2. """
    def __init__(self, player):
        Level.__init__(self, player)
        self.level_limit = -1000
        self.background_color = (40, 20, 60)

        level_platforms = [ [210, 30, 450, 570], [210, 30, 850, 420] ]
        for platform_data in level_platforms:
            block = Platform(platform_data[0], platform_data[1], (200,100,100))
            block.rect.x = platform_data[2]
            block.rect.y = platform_data[3]
            self.platform_list.add(block)

        goal = Goal(50, 50)
        goal.rect.x = 1200; goal.rect.y = 230
        self.goal.add(goal)