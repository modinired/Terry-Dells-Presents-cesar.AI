import pytest
import pygame
from lavacakes_pizza_fury.game.enemy import Enemy

@pytest.fixture
def enemy():
    """Provides a new Enemy instance for each test."""
    return Enemy(30, 50)

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

    # Move right for a few steps, but not enough to hit the boundary
    for _ in range(10):
        enemy.update()
    assert enemy.rect.x > 100
    assert enemy.change_x == 2 # Should still be moving right

    # Hit the right boundary and reverse
    enemy.rect.x = 201 # Place the enemy just past the boundary
    enemy.update()
    assert enemy.change_x == -2 # Should now be moving left

    # Hit the left boundary and reverse
    enemy.rect.x = 99 # Place the enemy just past the boundary
    enemy.update()
    assert enemy.change_x == 2 # Should now be moving right