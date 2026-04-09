import math
import pygame

from constants import CX, CY, RADIUS, PLAYER_ANGLE, JUMP_FORCE, GRAVITY, PLAYER_COL


class Player:
    """
    White dot fixed at the bottom of the circle.
    SPACE / UP / W makes it hop inward (upward on screen) to clear obstacles.
    """

    R     = 9            # visual + collision radius
    ANGLE = PLAYER_ANGLE

    def __init__(self) -> None:
        self.jump_h: float = 0.0   # pixels inward from the circle surface
        self.jump_v: float = 0.0   # current upward velocity

    # ── input ──────────────────────────────────────────────────────────────

    def jump(self) -> None:
        if self.jump_h == 0:        # only jump from the ground
            self.jump_v = float(JUMP_FORCE)

    # ── update ─────────────────────────────────────────────────────────────

    def update(self) -> None:
        if self.jump_v != 0 or self.jump_h > 0:
            self.jump_h += self.jump_v
            self.jump_v -= GRAVITY
            if self.jump_h <= 0:
                self.jump_h = 0.0
                self.jump_v = 0.0

    # ── geometry ───────────────────────────────────────────────────────────

    def screen_pos(self) -> tuple[int, int]:
        r = RADIUS - self.jump_h
        return (
            int(CX + r * math.cos(self.ANGLE)),
            int(CY + r * math.sin(self.ANGLE)),
        )

    # ── render ─────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, PLAYER_COL, self.screen_pos(), self.R)
