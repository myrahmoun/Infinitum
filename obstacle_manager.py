import random
import pygame

from constants import (
    INIT_SPEED, SPEED_DELTA,
    BASE_SPAWN_INT, MIN_SPAWN_INT, SPAWN_TIGHTEN,
    SPAWN_RAND_PCT, MIN_GAP_ANGLE,
    SPAWN_ANGLE,
)
from obstacle import Obstacle
from player import Player


class ObstacleManager:
    """Spawns, updates, and culls obstacles; owns the score counter."""

    def __init__(self) -> None:
        self.pool        : list[Obstacle] = []
        self.score       = 0
        self.spawn_timer = 0
        self.spawn_int   = BASE_SPAWN_INT
        self._next_spawn = BASE_SPAWN_INT   # randomised each time

    # ── helpers ────────────────────────────────────────────────────────────

    def _current_speed(self) -> float:
        return INIT_SPEED + self.score * SPEED_DELTA

    def _gap_ok(self) -> bool:
        """True when the most-recently-spawned obstacle is far enough ahead."""
        if not self.pool:
            return True
        last_angle = self.pool[-1].angle
        return (last_angle - SPAWN_ANGLE) >= MIN_GAP_ANGLE

    def _try_spawn(self) -> None:
        self.spawn_timer += 1
        if self.spawn_timer >= self._next_spawn and self._gap_ok():
            self.spawn_timer = 0
            extra = random.uniform(0, self.spawn_int * SPAWN_RAND_PCT)
            self._next_spawn = self.spawn_int + int(extra)
            self.pool.append(Obstacle(self._current_speed()))

    def _update_difficulty(self) -> None:
        self.spawn_int = max(
            MIN_SPAWN_INT,
            int(BASE_SPAWN_INT - self.score * SPAWN_TIGHTEN),
        )

    # ── main tick ──────────────────────────────────────────────────────────

    def update(self, player: Player) -> bool:
        """Tick every obstacle.  Returns True if any collision occurred."""
        self._try_spawn()
        hit = False
        for obs in self.pool[:]:
            if obs.update():        # True the frame the obstacle clears the player
                self.score += 1
                self._update_difficulty()
            if obs.collides(player):
                hit = True
            if not obs.alive:
                self.pool.remove(obs)
        return hit

    # ── render ─────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        for obs in self.pool:
            obs.draw(surface)
