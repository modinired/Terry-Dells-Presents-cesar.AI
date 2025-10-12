import pytest
import pygame
from lavacakes_pizza_fury.game.player import Player
from lavacakes_pizza_fury.game.level import Level, Platform

@pytest.fixture
def player():
    """Provides a new Player instance with no assets for testing."""
    player = Player(0, 0, sprite_sheet_path=None)
    player.level = Level(player)
    return player

def test_player_creation(player):
    """Tests that the player is created at the correct coordinates."""
    assert player.rect.x == 0
    assert player.rect.y == 0
    assert player.state == "idle"

def test_player_state_changes(player):
    """Tests that the player's state changes correctly."""
    player.go_right()
    player._set_state()
    assert player.state == "walking"
    player.stop()
    player._set_state()
    assert player.state == "idle"
    player.jump()
    player.change_y = -10
    player._set_state()
    assert player.state == "jumping"

def test_player_go_left(player):
    player.go_left()
    assert player.change_x == -6

def test_player_go_right(player):
    player.go_right()
    assert player.change_x == 6

def test_player_stop(player):
    player.go_left()
    player.stop()
    assert player.change_x == 0

def test_gravity(player):
    player.calc_grav()
    assert player.change_y > 0

def test_jump(player):
    platform = Platform(100, 20)
    player.level.platform_list.add(platform)
    player.rect.bottom = platform.rect.top
    player.jump()
    assert player.change_y == -10

def test_no_double_jump(player):
    platform = Platform(100, 20)
    player.level.platform_list.add(platform)
    player.rect.bottom = platform.rect.top
    player.jump()
    initial_speed = player.change_y
    player.rect.y -= 20
    player.jump()
    assert player.change_y == initial_speed

def test_collision_with_platform(player):
    platform = Platform(100, 20)
    platform.rect.x = 0
    platform.rect.y = 100
    player.level.platform_list.add(platform)

    player.rect.y = 50
    player.change_y = 50
    player.update()

    # Allow for a small overlap due to floating point inaccuracies
    assert abs(player.rect.bottom - platform.rect.top) < 5
    assert player.change_y == 0