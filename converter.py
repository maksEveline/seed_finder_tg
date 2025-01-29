from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import API, UseCurrentSession
import asyncio


async def main():

    # Load TDesktop client from tdata folder
    tdataFolder = "/Users/sixthjeez/Documents/GitHub/seed_finder_tg/1237602998/tdata"
    tdesk = TDesktop(tdataFolder)

    # Check if we have loaded any accounts
    assert tdesk.isLoaded()

    # flag=UseCurrentSession
    #
    # Convert TDesktop to Telethon using the current session.
    client = await tdesk.ToTelethon(session="telethon.session", flag=UseCurrentSession)

    # Connect and print all logged-in sessions of this client.
    # Telethon will save the session to telethon.session on creation.
    await client.connect()
    await client.PrintSessions()


asyncio.run(main())
