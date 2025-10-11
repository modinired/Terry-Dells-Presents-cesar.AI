import pytest
import pygame
from lavacakes_pizza_fury.game.level import Level_01
from lavacakes_pizza_fury.game.player import Player

@pytest.fixture
def level():
    """Provides a new Level_01 instance for each test."""
    player = Player(0, 0)
    level = Level_01(player)
    player.level = level # Make sure the player has a reference to the level
    return level

def test_level_creation(level):
    """Tests that the level is created with platforms."""
    assert len(level.platform_list.sprites()) > 0

def test_world_shift(level):
    """Tests that the world_shift method moves platforms correctly."""
    # Get the initial position of the first platform
    first_platform = level.platform_list.sprites()[0]
    initial_x = first_platform.rect.x

    # Shift the world
    level.shift_world(-100)

    # The platform should have moved
    assert first_platform.rect.x == initial_x - 100

    # The world_shift variable should be updated
    assert level.world_shift == -100