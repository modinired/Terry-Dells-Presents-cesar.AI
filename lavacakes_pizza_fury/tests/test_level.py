import pytest
import pygame
from lavacakes_pizza_fury.game.level import Level_01
from lavacakes_pizza_fury.game.player import Player

@pytest.fixture
def level():
    """Provides a new Level_01 instance with no assets for testing."""
    player = Player(0, 0, sprite_sheet_path=None)
    level = Level_01(player, background_paths=None)
    player.level = level
    return level

def test_level_creation(level):
    """Tests that the level is created with platforms."""
    assert len(level.platform_list.sprites()) > 0

def test_world_shift(level):
    """Tests that the world_shift method moves platforms correctly."""
    first_platform = level.platform_list.sprites()[0]
    initial_x = first_platform.rect.x

    level.shift_world(-100)

    assert first_platform.rect.x == initial_x - 100

    assert level.world_shift == -100