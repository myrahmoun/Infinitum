import math
import random
import pygame

from constants import (
    CX, CY, RADIUS,
    PLAYER_ANGLE, SPAWN_ANGLE,
    OBS_HALF_W_RANGE, OBS_HEIGHT_RANGE,
    SHADOW_FADE_IN, SHADOW_FADE_OUT,
    OBS_COL,
)
from player import Player


class Obstacle:
    """
    A peg-shaped obstacle that travels clockwise along the circle rim,
    from the spawn zone (top) all the way back around to it again.
    The peg points radially inward so it is visible against the circle fill.
    Dimensions (width / height) are randomised on creation.
    """

    def __init__(self, speed: float) -> None:
        self.angle   = SPAWN_ANGLE
        self.speed   = speed
        self.alive   = True
        self._passed = False            # True once it has cleared the player

        self.half_w = random.randint(*OBS_HALF_W_RANGE)   # tangential half-width
        self.height = random.randint(*OBS_HEIGHT_RANGE)   # radial height
        self.cr     = max(self.half_w, self.height // 2)  # collision radius

    # ── update ─────────────────────────────────────────────────────────────

    def update(self) -> bool:
        """Advance one frame.  Returns True the first frame it clears the player."""
        self.angle += self.speed

        just_scored = False
        if not self._passed and self.angle > PLAYER_ANGLE + 0.15:
            self._passed = True
            just_scored  = True

        # Die once back inside the spawn-zone shadow
        if self.angle > SPAWN_ANGLE + 2 * math.pi - SHADOW_FADE_OUT * 0.5:
            self.alive = False

        return just_scored

    # ── geometry ───────────────────────────────────────────────────────────

    def screen_pos(self) -> tuple[int, int]:
        """Centre of the peg base on the circle surface."""
        return (
            int(CX + RADIUS * math.cos(self.angle)),
            int(CY + RADIUS * math.sin(self.angle)),
        )

    def collides(self, player: Player) -> bool:
        if not self.alive:
            return False
        px, py = player.screen_pos()
        ox, oy = self.screen_pos()
        return math.hypot(px - ox, py - oy) < player.R + self.cr

    # ── render ─────────────────────────────────────────────────────────────

    def _visible(self) -> bool:
        """Hidden inside the spawn shadow at both ends of the journey."""
        return (
            SPAWN_ANGLE + SHADOW_FADE_IN
            < self.angle <
            SPAWN_ANGLE + 2 * math.pi - SHADOW_FADE_OUT
        )

    def draw(self, surface: pygame.Surface) -> None:
        if not self._visible():
            return

        x, y   = self.screen_pos()
        ca, sa = math.cos(self.angle), math.sin(self.angle)
        rx, ry = -ca, -sa   # inward radial direction
        tx, ty = -sa,  ca   # tangential direction

        pts = [
            (x - self.half_w * tx,                   y - self.half_w * ty),
            (x + self.half_w * tx,                   y + self.half_w * ty),
            (x + self.half_w * tx + self.height * rx, y + self.half_w * ty + self.height * ry),
            (x - self.half_w * tx + self.height * rx, y - self.half_w * ty + self.height * ry),
        ]
        pygame.draw.polygon(
            surface, OBS_COL,
            [(int(p[0]), int(p[1])) for p in pts],
        )
