import pytest
from lavacakes_pizza_fury.game.player import Player

def test_import():
    """
    This test simply tries to import the main module.
    If this fails, there's a problem with the setup or dependencies.
    """
    try:
        import lavacakes_pizza_fury.main
    except ImportError as e:
        assert False, f"Failed to import the main game module: {e}"

@pytest.fixture
def player():
    """Provides a new Player instance for each test."""
    return Player(0, 0)

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
    player.go_left() # Start moving first
    player.stop()
    assert player.change_x == 0

def test_player_update(player):
    """Tests that the update method moves the player correctly."""
    player.go_right()
    player.update()
    assert player.rect.x == 5
    player.update()
    assert player.rect.x == 10