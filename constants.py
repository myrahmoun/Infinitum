import math

# ─── Display ──────────────────────────────────────────────────────────────────

WIDTH, HEIGHT = 800, 800
FPS           = 60

# ─── Colors ───────────────────────────────────────────────────────────────────

BG         = (10,  10,  15)
CIRCLE_COL = (22,  22,  32)
RING_COL   = (50,  50,  68)
PLAYER_COL = (230, 230, 235)
OBS_COL    = (210,  60,  60)
TEXT_COL   = (170, 170, 188)

# ─── World geometry ───────────────────────────────────────────────────────────

CX, CY = WIDTH // 2, HEIGHT // 2
RADIUS = 270

PLAYER_ANGLE = math.pi / 2     # south – bottom of circle (fixed)
SPAWN_ANGLE  = -math.pi / 2    # north – top of circle   (diametrically opposite)

# ─── Jump physics ─────────────────────────────────────────────────────────────
# Player moves *inward* (upward on screen at the bottom) to clear obstacles.

JUMP_FORCE = 12
GRAVITY    = 0.65

# ─── Obstacle geometry ────────────────────────────────────────────────────────
# Dimensions are randomised per obstacle within these ranges.

OBS_HALF_W_RANGE = (4,  14)   # tangential half-width → "short / long"
OBS_HEIGHT_RANGE = (12, 38)   # radial height         → "low / high"

# Shadow fade margins (radians from SPAWN_ANGLE) – obstacles are hidden while
# inside the dark spawn-zone vignette, both on the way out and on return.
SHADOW_FADE_IN  = 0.22
SHADOW_FADE_OUT = 0.22

# ─── Difficulty ramp ──────────────────────────────────────────────────────────

INIT_SPEED     = 0.020    # radians per frame
SPEED_DELTA    = 0.000014
BASE_SPAWN_INT = 145      # base frames between spawns at score 0
MIN_SPAWN_INT  = 55
SPAWN_TIGHTEN  = 0.12     # frames subtracted per point scored
SPAWN_RAND_PCT = 0.55     # random extra delay as fraction of spawn_int (0 → 55% more)
MIN_GAP_ANGLE  = 1.15     # min angular gap (radians) between consecutive obstacles
