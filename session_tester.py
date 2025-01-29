import asyncio
from telethon import TelegramClient

api_id = 22958441
api_hash = "330d700e87105b18835fd8d325d7d997"
session_name = "converted_sessions/1692843096.session"


async def get_account_id():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        me = await client.get_me()
        print(me.id)


asyncio.run(get_account_id())
