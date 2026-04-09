"""
Headless tests for Infinitum.
Run with:  python test_game.py
Uses SDL_VIDEODRIVER=dummy so no window is opened.
"""

import math
import os
import sys
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((800, 800))   # required before Surface calls

from constants import (
    SPAWN_ANGLE, PLAYER_ANGLE, RADIUS, CX, CY,
    JUMP_FORCE, GRAVITY,
    OBS_HALF_W_RANGE, OBS_HEIGHT_RANGE,
    BASE_SPAWN_INT, MIN_SPAWN_INT, INIT_SPEED,
)
from player import Player
from obstacle import Obstacle
from obstacle_manager import ObstacleManager
from world_circle import WorldCircle


# ─── Player ───────────────────────────────────────────────────────────────────

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player()

    def test_initial_position_on_circle(self):
        x, y = self.player.screen_pos()
        # Player should sit on the circle's bottom edge
        self.assertAlmostEqual(x, CX, delta=1)
        self.assertAlmostEqual(y, CY + RADIUS, delta=1)

    def test_jump_moves_player_inward(self):
        self.player.jump()
        self.player.update()
        _, y = self.player.screen_pos()
        # After one frame the player should be above (lower y) the circle edge
        self.assertLess(y, CY + RADIUS)

    def test_no_double_jump(self):
        self.player.jump()
        v_after_first = self.player.jump_v
        self.player.jump()          # second press mid-air – should be ignored
        self.assertEqual(self.player.jump_v, v_after_first)

    def test_player_returns_to_ground(self):
        self.player.jump()
        for _ in range(200):        # run long enough to land
            self.player.update()
        self.assertAlmostEqual(self.player.jump_h, 0.0)
        self.assertAlmostEqual(self.player.jump_v, 0.0)

    def test_jump_clears_minimum_height(self):
        self.player.jump()
        max_h = 0.0
        for _ in range(200):
            self.player.update()
            max_h = max(max_h, self.player.jump_h)
        # Must clear at least the tallest possible obstacle height
        self.assertGreater(max_h, OBS_HEIGHT_RANGE[1])


# ─── Obstacle ─────────────────────────────────────────────────────────────────

class TestObstacle(unittest.TestCase):

    def _make(self, speed=INIT_SPEED):
        return Obstacle(speed)

    def test_spawns_at_spawn_angle(self):
        obs = self._make()
        self.assertAlmostEqual(obs.angle, SPAWN_ANGLE)

    def test_dimensions_in_range(self):
        for _ in range(50):
            obs = self._make()
            self.assertGreaterEqual(obs.half_w, OBS_HALF_W_RANGE[0])
            self.assertLessEqual(obs.half_w,    OBS_HALF_W_RANGE[1])
            self.assertGreaterEqual(obs.height, OBS_HEIGHT_RANGE[0])
            self.assertLessEqual(obs.height,    OBS_HEIGHT_RANGE[1])

    def test_advances_each_frame(self):
        obs = self._make(speed=0.05)
        obs.update()
        self.assertAlmostEqual(obs.angle, SPAWN_ANGLE + 0.05)

    def test_scores_exactly_once(self):
        obs = self._make(speed=0.1)
        scored_count = 0
        for _ in range(300):
            if obs.update():
                scored_count += 1
        self.assertEqual(scored_count, 1)

    def test_dies_near_spawn_zone(self):
        obs = self._make(speed=0.1)
        for _ in range(2000):
            obs.update()
            if not obs.alive:
                break
        self.assertFalse(obs.alive)
        # Should die close to completing a full loop
        full_loop = SPAWN_ANGLE + 2 * math.pi
        self.assertLess(abs(obs.angle - full_loop), 0.5)

    def test_not_visible_at_spawn(self):
        obs = self._make()
        self.assertFalse(obs._visible())

    def test_becomes_visible_after_shadow(self):
        obs = self._make(speed=0.1)
        # Advance past the fade-in threshold
        for _ in range(30):
            obs.update()
        self.assertTrue(obs._visible())

    def test_collision_with_grounded_player(self):
        player = Player()                   # on the circle edge, not jumping
        obs    = self._make(speed=0.1)
        # Teleport obstacle to the player's angle
        obs.angle = PLAYER_ANGLE
        self.assertTrue(obs.collides(player))

    def test_no_collision_when_player_jumps_high(self):
        player = Player()
        player.jump()
        for _ in range(15):                 # reach near peak height
            player.update()

        obs       = self._make()
        obs.angle = PLAYER_ANGLE            # worst-case position
        # Even the tallest obstacle should be cleared at peak jump
        obs.height = OBS_HEIGHT_RANGE[1]
        obs.cr     = max(obs.half_w, obs.height // 2)
        self.assertFalse(obs.collides(player))


# ─── ObstacleManager ─────────────────────────────────────────────────────────

class TestObstacleManager(unittest.TestCase):

    def setUp(self):
        self.mgr    = ObstacleManager()
        self.player = Player()

    def test_no_spawn_before_interval(self):
        for _ in range(BASE_SPAWN_INT - 1):
            self.mgr.update(self.player)
        self.assertEqual(len(self.mgr.pool), 0)

    def test_spawns_at_interval(self):
        for _ in range(BASE_SPAWN_INT):
            self.mgr.update(self.player)
        self.assertEqual(len(self.mgr.pool), 1)

    def test_score_increments_on_clear(self):
        # Spawn one fast obstacle and let it pass the player
        self.mgr.pool.append(Obstacle(speed=0.5))
        for _ in range(200):
            self.mgr.update(self.player)
            if self.mgr.score > 0:
                break
        self.assertEqual(self.mgr.score, 1)

    def test_spawn_interval_decreases_with_score(self):
        initial_int = self.mgr.spawn_int
        self.mgr.score = 50
        self.mgr._update_difficulty()
        self.assertLess(self.mgr.spawn_int, initial_int)

    def test_spawn_interval_never_below_minimum(self):
        self.mgr.score = 10_000
        self.mgr._update_difficulty()
        self.assertGreaterEqual(self.mgr.spawn_int, MIN_SPAWN_INT)

    def test_dead_obstacles_are_removed(self):
        obs       = Obstacle(speed=0.1)
        obs.alive = False
        self.mgr.pool.append(obs)
        self.mgr.update(self.player)
        self.assertNotIn(obs, self.mgr.pool)

    def test_returns_true_on_collision(self):
        # update() advances the angle *before* the collision check, so start
        # just before PLAYER_ANGLE so the obstacle lands on the player after
        # the first step.
        obs       = Obstacle(speed=0.1)
        obs.angle = PLAYER_ANGLE - 0.05
        self.mgr.pool.append(obs)
        hit = self.mgr.update(self.player)
        self.assertTrue(hit)


# ─── WorldCircle ─────────────────────────────────────────────────────────────

class TestWorldCircle(unittest.TestCase):

    def test_instantiates_without_error(self):
        wc = WorldCircle()
        self.assertIsNotNone(wc._shadow)

    def test_shadow_surface_correct_size(self):
        wc = WorldCircle()
        self.assertEqual(wc._shadow.get_size(), (800, 800))

    def test_draw_does_not_raise(self):
        wc   = WorldCircle()
        surf = pygame.display.get_surface()
        wc.draw(surf)               # should complete without exception


# ─── entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
