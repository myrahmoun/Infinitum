import sys
import pygame

from constants import WIDTH, HEIGHT, FPS, BG, TEXT_COL
from world_circle import WorldCircle
from player import Player
from obstacle_manager import ObstacleManager


class Game:
    """Top-level controller: event loop, state machine, rendering."""

    def __init__(self) -> None:
        pygame.init()
        self.screen  = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Infinitum")
        self.clock   = pygame.time.Clock()
        self.font_xl = pygame.font.Font(None, 80)
        self.font_md = pygame.font.Font(None, 40)
        self.font_sm = pygame.font.Font(None, 30)
        self._reset()

    # ── state ──────────────────────────────────────────────────────────────

    def _reset(self) -> None:
        self.world   = WorldCircle()
        self.player  = Player()
        self.obs_mgr = ObstacleManager()
        self.state   = "playing"    # "playing" | "dead"

    # ── events ─────────────────────────────────────────────────────────────

    def _handle_events(self) -> None:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if self.state == "playing":
                        self.player.jump()
                    else:
                        self._reset()
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    # ── update ─────────────────────────────────────────────────────────────

    def _update(self) -> None:
        if self.state != "playing":
            return
        self.player.update()
        if self.obs_mgr.update(self.player):
            self.state = "dead"

    # ── rendering ──────────────────────────────────────────────────────────

    def _blit_center(self, surf: pygame.Surface, cy: int) -> None:
        self.screen.blit(surf, surf.get_rect(center=(WIDTH // 2, cy)))

    def _draw_hud(self) -> None:
        self._blit_center(
            self.font_md.render(str(self.obs_mgr.score), True, TEXT_COL), 34
        )

    def _draw_game_over(self) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        self.screen.blit(overlay, (0, 0))

        mid = HEIGHT // 2
        for text, font, dy, color in (
            ("GAME OVER",                       self.font_xl, -48, (220, 60, 60)),
            (f"Score  {self.obs_mgr.score}",    self.font_md,  18, TEXT_COL),
            ("SPACE  /  UP  /  W  to restart",  self.font_sm,  60, (110, 110, 128)),
        ):
            self._blit_center(font.render(text, True, color), mid + dy)

    def _draw(self) -> None:
        self.screen.fill(BG)
        self.world.draw(self.screen)
        self.obs_mgr.draw(self.screen)
        self.player.draw(self.screen)
        self._draw_hud()
        if self.state == "dead":
            self._draw_game_over()
        pygame.display.flip()

    # ── loop ───────────────────────────────────────────────────────────────

    def step(self) -> None:
        """Advance one frame. Called by the async loop in main.py."""
        self._handle_events()
        self._update()
        self._draw()
        self.clock.tick(FPS)

    def run(self) -> None:
        while True:
            self.step()
