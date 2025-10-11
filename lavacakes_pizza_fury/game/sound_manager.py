import pygame

class SoundManager:
    """
    A professional, centralized class for managing all sound and music in the game.
    This manager is designed to be robust and fail-safe. If a sound or music
    file cannot be loaded, it will print a warning but will not crash the game.
    """

    def __init__(self):
        """ Initializes the SoundManager. """
        self.sounds = {}

    def load_sound(self, name, path):
        """
        Loads a sound effect from a file and stores it.

        Args:
            name (str): The name to associate with the sound (e.g., 'jump').
            path (str): The file path to the sound effect.
        """
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
        except pygame.error as e:
            print(f"Warning: Could not load sound '{name}' from '{path}'. Error: {e}")
            self.sounds[name] = None

    def play_sound(self, name):
        """
        Plays a loaded sound effect.
        If the sound was not loaded successfully, this method does nothing.

        Args:
            name (str): The name of the sound to play.
        """
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play()
        else:
            print(f"Info: Sound '{name}' not played (was not loaded).")

    def load_music(self, path):
        """
        Loads a music track from a file.

        Args:
            path (str): The file path to the music track.
        """
        try:
            pygame.mixer.music.load(path)
        except pygame.error as e:
            print(f"Warning: Could not load music from '{path}'. Error: {e}")

    def play_music(self, loops=-1):
        """
        Plays the loaded music track.

        Args:
            loops (int, optional): The number of times to repeat the music.
                                   -1 makes it loop indefinitely. Defaults to -1.
        """
        try:
            pygame.mixer.music.play(loops)
        except pygame.error as e:
            print(f"Warning: Could not play music. Error: {e}")

    def stop_music(self):
        """ Stops the currently playing music. """
        pygame.mixer.music.stop()