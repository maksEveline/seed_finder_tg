from opentele.td import TDesktop
from opentele.api import UseCurrentSession
import asyncio
import os


async def process_account(account_folder, sessions_folder):
    tdata_path = os.path.join("tdatas", account_folder, "tdata")
    if not os.path.exists(tdata_path):
        print(f"Папка {account_folder} не найдена")
        return

    tdesk = TDesktop(tdata_path)
    if not tdesk.isLoaded():
        print(f"Папка {account_folder} не загружена")
        return

    session_path = os.path.join(sessions_folder, f"{account_folder}.session")
    client = await tdesk.ToTelethon(session=session_path, flag=UseCurrentSession)

    await client.connect()
    await client.PrintSessions()
    await client.disconnect()


async def main():
    base_folder = "tdatas"
    sessions_folder = "converted_sessions"
    os.makedirs(sessions_folder, exist_ok=True)

    accounts = [
        d
        for d in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, d))
    ]

    tasks = [process_account(account, sessions_folder) for account in accounts]
    await asyncio.gather(*tasks)

    print(f"Конвертация завершена\nОбработано {len(accounts)} аккаунтов.")


asyncio.run(main())
