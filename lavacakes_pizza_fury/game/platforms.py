import pygame

class Platform(pygame.sprite.Sprite):
    """
    Represents a platform in the game world.

    This class defines the solid surfaces that the player can stand on and
    interact with. It is built upon pygame's Sprite class, which allows it
    to be easily added to sprite groups for efficient rendering and
    collision detection.
    """
    def __init__(self, width, height, color=(0, 255, 0)):
        """
        Initializes the platform sprite.

        Args:
            width (int): The width of the platform in pixels.
            height (int): The height of the platform in pixels.
            color (tuple, optional): The RGB color of the platform.
                                     Defaults to green.
        """
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        self.rect = self.image.get_rect()