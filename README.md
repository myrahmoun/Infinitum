# Infinitum

An endless-runner built with **pygame** where a circular world rotates toward you.

## Gameplay

A dark circle fills the screen. Your dot sits fixed at the bottom. Obstacles are spawned
in a shadowed zone at the top (diametrically opposite you), emerge as the circle rotates
clockwise, and must be jumped over before they reach your position. Survive as long as
possible — speed and spawn-rate increase with your score.

## Controls

| Key | Action |
|-----|--------|
| `SPACE` / `UP` / `W` | Jump |
| `SPACE` / `UP` / `W` | Restart (after death) |
| `ESC` | Quit |

## Setup

```bash
python -m venv env
source env/bin/activate      # Windows: env\Scripts\activate
pip install pygame
python main.py
```

## Project structure

```
infinitum/
├── main.py              # entry point
├── game.py              # Game – event loop, state machine, rendering
├── world_circle.py      # WorldCircle – static circle + spawn-zone shadow
├── player.py            # Player – jump physics and drawing
├── obstacle.py          # Obstacle – travel, collision, drawing
├── obstacle_manager.py  # ObstacleManager – spawning, scoring, difficulty
└── constants.py         # all tunable values (speed, sizes, colors …)
```
