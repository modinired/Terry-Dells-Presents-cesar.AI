import pygame

class Player(pygame.sprite.Sprite):
    """
    Represents the player character in Lavacakes: Pizza Fury.

    This class handles the player's appearance, movement, and interactions
    within the game world. It is built upon pygame's Sprite class to leverage
    powerful, built-in rendering and collision detection features.
    """
    def __init__(self, x, y):
        """
        Initializes the player sprite.

        Args:
            x (int): The initial x-coordinate of the player's top-left corner.
            y (int): The initial y-coordinate of the player's top-left corner.
        """
        super().__init__()

        # --- Create a Placeholder Image ---
        # We are creating a simple, multi-colored sprite programmatically.
        # This serves as a clear placeholder and makes it easy to replace with
        # final art later without changing any game logic.
        self.image = pygame.Surface([40, 60])
        self.image.set_colorkey((0,0,0)) # Make black transparent

        # Body (Blue)
        pygame.draw.rect(self.image, (0, 0, 255), [10, 20, 20, 40])
        # Head (Green)
        pygame.draw.circle(self.image, (0, 255, 0), (20, 10), 10)


        # The 'rect' is essential for positioning and collision detection.
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # --- Movement Properties ---
        # The player's current speed vector.
        self.change_x = 0
        self.change_y = 0

    def update(self):
        """
        Update the player's position based on the current speed vector.
        This method is called once per frame and handles all movement logic.
        """
        # In a real platformer, gravity would be applied here.
        # For now, we'll just update the horizontal position.
        self.rect.x += self.change_x

    def go_left(self):
        """Sets the player's speed to move left."""
        self.change_x = -5

    def go_right(self):
        """Sets the player's speed to move right."""
        self.change_x = 5

    def stop(self):
        """Stops the player's horizontal movement."""
        self.change_x = 0