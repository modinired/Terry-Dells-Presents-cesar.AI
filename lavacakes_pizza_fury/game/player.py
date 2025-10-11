import pygame

class Player(pygame.sprite.Sprite):
    """
    Represents the player character in Lavacakes: Pizza Fury.
    """
    def __init__(self, x, y):
        """
        Initializes the player sprite.
        """
        super().__init__()

        self.image = pygame.Surface([40, 60])
        self.image.set_colorkey((0,0,0))

        pygame.draw.rect(self.image, (0, 0, 255), [10, 20, 20, 40])
        pygame.draw.circle(self.image, (0, 255, 0), (20, 10), 10)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.change_x = 0
        self.change_y = 0

        self.level = None

    def update(self):
        """ Update the player's position. """
        self.calc_grav()

        # --- Horizontal Movement & Collision ---
        self.rect.x += self.change_x
        block_hit_list = pygame.sprite.spritecollide(self, self.level, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right

        # --- Vertical Movement & Collision ---
        self.rect.y += self.change_y
        block_hit_list = pygame.sprite.spritecollide(self, self.level, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
            self.change_y = 0

    def calc_grav(self):
        """ Calculates the effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35

    def jump(self):
        """ Called when user hits the 'jump' button. """
        # To prevent double-jumping, we'll only allow a jump if the player is
        # near the ground. We check this by seeing if they can collide with a
        # platform below them.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level, False)
        self.rect.y -= 2

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= 600:
            self.change_y = -10

    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -5

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 5

    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0