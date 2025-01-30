import asyncio
from random import randint


async def random_delay(min_delay=1, max_delay=3):
    delay = randint(0.5, 1)
    await asyncio.sleep(delay)
