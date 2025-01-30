import asyncio
import os
import json
import random
import shutil
from opentele.td import TDesktop
from opentele.api import UseCurrentSession


donor_folder = "donor_jsons"
converted_folder = "converted_sessions"
base_folder = "tdatas"


def get_random_donor_json():
    donor_files = [f for f in os.listdir(donor_folder) if f.endswith(".json")]
    if not donor_files:
        raise FileNotFoundError("Нет доступных donor JSON файлов.")
    return os.path.join(donor_folder, random.choice(donor_files))


async def process_account(account_folder):
    tdata_path = os.path.join(base_folder, account_folder, "tdata")
    if not os.path.exists(tdata_path):
        print(f"Папка {account_folder} не найдена")
        return

    tdesk = TDesktop(tdata_path)
    if not tdesk.isLoaded():
        print(f"Папка {account_folder} не загружена")
        return

    session_path = os.path.join(converted_folder, f"{account_folder}.session")
    client = await tdesk.ToTelethon(session=session_path, flag=UseCurrentSession)
    await client.connect()
    await client.disconnect()

    donor_json_path = get_random_donor_json()
    new_json_path = os.path.join(converted_folder, f"{account_folder}.json")
    shutil.copy(donor_json_path, new_json_path)


async def main():
    os.makedirs(converted_folder, exist_ok=True)

    accounts = [
        d
        for d in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, d))
    ]
    tasks = [process_account(account) for account in accounts]
    await asyncio.gather(*tasks)

    print(f"Конвертация завершена. Обработано {len(accounts)} аккаунтов.")


asyncio.run(main())
