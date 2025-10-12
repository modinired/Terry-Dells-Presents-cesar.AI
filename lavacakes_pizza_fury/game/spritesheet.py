import pygame

class SpriteSheet:
    """
    A utility class for loading and parsing sprite sheets.
    """

    def __init__(self, filename):
        """
        Constructor. Pass in the file name of the sprite sheet.
        """
        self.sprite_sheet = None
        if filename:
            try:
                self.sprite_sheet = pygame.image.load(filename).convert()
            except pygame.error as e:
                print(f"Warning: Unable to load spritesheet image: {filename}. Error: {e}")

    def get_image(self, x, y, width, height):
        """
        Grabs a single image out of a larger spritesheet.
        """
        if not self.sprite_sheet:
            return None

        image = pygame.Surface([width, height]).convert()
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey((0, 0, 0))
        return image