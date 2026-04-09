import math
import pygame

from constants import (
    WIDTH, HEIGHT,
    CX, CY, RADIUS,
    SPAWN_ANGLE,
    CIRCLE_COL, RING_COL,
)


class WorldCircle:
    """The circular track.  Purely visual – no physics live here."""

    def __init__(self) -> None:
        self._shadow = self._build_shadow()

    @staticmethod
    def _build_shadow() -> pygame.Surface:
        """Pre-render a dark vignette over the spawn zone so obstacles
        emerge from (and disappear back into) shadow."""
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        sx = int(CX + RADIUS * math.cos(SPAWN_ANGLE))
        sy = int(CY + RADIUS * math.sin(SPAWN_ANGLE))
        for r, a in [(100, 170), (70, 140), (44, 110), (24, 80)]:
            pygame.draw.circle(surf, (8, 8, 12, a), (sx, sy), r)
        return surf

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, CIRCLE_COL, (CX, CY), RADIUS)
        pygame.draw.circle(surface, RING_COL,   (CX, CY), RADIUS, 2)
        surface.blit(self._shadow, (0, 0))
