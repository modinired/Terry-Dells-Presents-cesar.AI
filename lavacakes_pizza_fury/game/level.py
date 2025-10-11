import pygame

class Platform(pygame.sprite.Sprite):
    """
    Represents a platform in the game world.
    This class defines the solid surfaces that the player can stand on and
    interact with.
    """
    def __init__(self, width, height, color=(0, 255, 0)):
        """
        Initializes the platform sprite.
        """
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()


class Level():
    """
    This is a generic super-class used to define a level.
    Create a child class for each level with level-specific info.
    """
    def __init__(self, player):
        """
        Constructor. Pass in a handle to player.
        """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player
        self.world_shift = 0

    def update(self):
        """ Update everything on this level."""
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        """ Draw everything on this level. """
        screen.fill((0,0,0)) # Black background
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll everything: """
        self.world_shift += shift_x
        for platform in self.platform_list:
            platform.rect.x += shift_x
        for enemy in self.enemy_list:
            enemy.rect.x += shift_x


class Level_01(Level):
    """ Definition for level 1. """
    def __init__(self, player):
        """ Create level 1. """
        Level.__init__(self, player)
        self.level_limit = -1500

        level = [ [2000, 70, 0, 580],   # Ground
                  [210, 70, 500, 500],
                  [210, 70, 800, 400],
                  [210, 70, 1000, 500],
                  [210, 70, 1120, 280],
                ]

        for platform_data in level:
            block = Platform(platform_data[0], platform_data[1])
            block.rect.x = platform_data[2]
            block.rect.y = platform_data[3]
            block.player = self.player
            self.platform_list.add(block)