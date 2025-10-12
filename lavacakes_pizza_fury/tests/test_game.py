import pytest
import pygame
from lavacakes_pizza_fury.game.player import Player
from lavacakes_pizza_fury.game.level import Level, Platform

@pytest.fixture(scope="module")
def pygame_init():
    """Initializes pygame for the test module."""
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def player(pygame_init):
    """Provides a new Player instance with no assets for testing."""
    player = Player(0, 50)
    player.level = Level(player)
    return player

def test_player_creation(player):
    """Tests that the player is created at the correct coordinates."""
    assert player.pos.x == 0
    assert player.pos.y == 50
    player.update()
    assert player.state == "jumping"

def test_player_state_changes(player):
    """Tests that the player's state changes correctly by simulating the game loop."""
    # --- Land on a platform ---
    platform = Platform(200, 20)
    platform.rect.x = -50; platform.rect.y = 100
    player.level.platform_list.add(platform)
    for _ in range(20): player.update()
    assert player.on_ground, "Player should be on the ground after falling"
    assert player.state == "idle", "Player should be idle after landing"

    # --- Start walking ---
    for _ in range(10):
        player.go_right()
        player.update()
    assert player.state == "walking", "Player should be walking after moving"

    # --- Stop walking ---
    for _ in range(30):
        player.stop()
        player.update()
    assert player.state == "idle", "Player should be idle after stopping"

    # --- Jump ---
    player.on_ground = True
    player.jump()
    player.update()
    assert player.state == "jumping", "Player should be jumping after jump()"

def test_player_go_left(player):
    player.go_left()
    player.update()
    assert player.acc.x < 0

def test_player_go_right(player):
    player.go_right()
    player.update()
    assert player.acc.x > 0

def test_player_stop(player):
    player.go_right()
    player.update()
    player.stop()
    player.update()
    assert player.acc.x == 0

def test_gravity(player):
    player.update()
    assert player.vel.y > 0

def test_jump(player):
    player.on_ground = True
    player.jump()
    assert player.vel.y == -10

def test_no_double_jump(player):
    player.on_ground = True
    player.jump()
    initial_speed = player.vel.y
    player.on_ground = False
    player.jump()
    assert player.vel.y == initial_speed

def test_collision_with_platform(player):
    platform = Platform(100, 20)
    platform.rect.x = 0
    platform.rect.y = 100
    player.level.platform_list.add(platform)

    player.pos.y = 50
    player.vel.y = 10

    for _ in range(20):
        player.update()

    assert player.on_ground is True
    assert abs(player.rect.bottom - platform.rect.top) < 5
    assert player.vel.y == 0