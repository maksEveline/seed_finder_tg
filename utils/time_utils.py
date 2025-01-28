import asyncio
from random import randint


async def random_delay(min_delay=1, max_delay=3):
    delay = randint(min_delay, max_delay)
    await asyncio.sleep(delay)
