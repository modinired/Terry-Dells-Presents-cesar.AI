import pytest
import pygame
from lavacakes_pizza_fury.game.player import Player
from lavacakes_pizza_fury.game.level import Level, Platform

@pytest.fixture
def player():
    """Provides a new Player instance with a proper Level object."""
    player = Player(0, 0)
    player.level = Level(player)
    return player

def test_player_creation(player):
    """Tests that the player is created at the correct coordinates."""
    assert player.rect.x == 0
    assert player.rect.y == 0

def test_player_go_left(player):
    """Tests that the go_left method sets the correct speed."""
    player.go_left()
    assert player.change_x == -5

def test_player_go_right(player):
    """Tests that the go_right method sets the correct speed."""
    player.go_right()
    assert player.change_x == 5

def test_player_stop(player):
    """Tests that the stop method sets the speed to zero."""
    player.go_left()
    player.stop()
    assert player.change_x == 0

def test_player_update_horizontal_movement(player):
    """Tests that the update method moves the player correctly."""
    player.go_right()
    player.update()
    assert player.rect.x == 5
    player.update()
    assert player.rect.x == 10

def test_gravity(player):
    """Tests that the player is affected by gravity."""
    player.calc_grav()
    assert player.change_y > 0

    initial_y_change = player.change_y
    player.calc_grav()
    assert player.change_y > initial_y_change

def test_jump(player):
    """Tests that the player can jump when on a platform."""
    platform = Platform(100, 20)
    platform.rect.x = 0
    platform.rect.y = 100
    player.level.platform_list.add(platform)

    player.rect.bottom = platform.rect.top

    player.jump()
    assert player.change_y == -10

def test_no_double_jump(player):
    """Tests that the player cannot jump while in the air."""
    platform = Platform(100, 20)
    platform.rect.x = 0
    platform.rect.y = 100
    player.level.platform_list.add(platform)
    player.rect.bottom = platform.rect.top

    player.jump()
    assert player.change_y == -10

    player.rect.y -= 20

    player.jump()

    assert player.change_y == -10

def test_collision_with_platform(player):
    """Tests that the player stops on top of a platform."""
    platform = Platform(100, 20)
    platform.rect.x = 0
    platform.rect.y = 100
    player.level.platform_list.add(platform)

    player.rect.x = 0
    player.rect.y = 50
    player.change_y = 5

    player.update()

    assert player.rect.bottom == platform.rect.top
    assert player.change_y == 0