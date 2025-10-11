import pygame

class Enemy(pygame.sprite.Sprite):
    """
    Represents a basic enemy in the game.

    This class defines an enemy that patrols back and forth between two
    set boundaries. It is built upon pygame's Sprite class for efficient
    rendering and collision detection.
    """

    def __init__(self, width, height, color=(128, 0, 128)): # Purple
        """
        Initializes the enemy sprite.

        Args:
            width (int): The width of the enemy in pixels.
            height (int): The height of the enemy in pixels.
            color (tuple, optional): The RGB color of the enemy.
                                     Defaults to purple.
        """
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

        # --- Movement Properties ---
        self.change_x = 2
        self.boundary_top = 0
        self.boundary_bottom = 0
        self.boundary_left = 0
        self.boundary_right = 0
        self.level = None

    def update(self):
        """
        Update the enemy's position and behavior.
        This method is called once per frame.
        """
        # Move left/right
        self.rect.x += self.change_x

        # Check if we've hit the player
        # (This will be handled in the main game loop)

        # Check boundaries and reverse direction if needed
        if self.rect.right > self.boundary_right or self.rect.left < self.boundary_left:
            self.change_x *= -1