import asyncio
import pygame
from game import Game


async def main() -> None:
    game = Game()
    while True:
        game.step()
        await asyncio.sleep(0)  # yield control to the browser each frame


if __name__ == "__main__":
    asyncio.run(main())
