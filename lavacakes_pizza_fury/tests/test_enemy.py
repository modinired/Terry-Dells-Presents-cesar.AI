import pytest
import pygame
from lavacakes_pizza_fury.game.enemy import Enemy
from lavacakes_pizza_fury.game.level import Level
from lavacakes_pizza_fury.game.player import Player

@pytest.fixture
def enemy():
    """Provides a new Enemy instance with no assets for testing."""
    enemy = Enemy(30, 50, sprite_sheet_path=None)
    player = Player(0, 0, sprite_sheet_path=None)
    enemy.level = Level(player)
    return enemy

def test_enemy_creation(enemy):
    """Tests that the enemy is created with default values."""
    assert enemy.rect.width == 30
    assert enemy.rect.height == 50
    assert enemy.change_x == 2

def test_enemy_patrol(enemy):
    """Tests that the enemy patrols back and forth."""
    enemy.boundary_left = 100
    enemy.boundary_right = 200
    enemy.rect.x = 100

    for _ in range(10):
        enemy.update()
    assert enemy.rect.x > 100
    assert enemy.change_x == 2

    enemy.rect.x = 201
    enemy.update()
    assert enemy.change_x == -2

    enemy.rect.x = 99
    enemy.update()
    assert enemy.change_x == 2