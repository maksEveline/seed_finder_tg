import asyncio
import os
import random
import shutil
from opentele.td import TDesktop
from opentele.api import UseCurrentSession
from opentele.exception import OpenTeleException


donor_folder = "donor_jsons"
converted_folder = "converted_sessions"
base_folder = "tdatas"
successful = 0
failed = 0


def get_random_donor_json():
    donor_files = [f for f in os.listdir(donor_folder) if f.endswith(".json")]
    if not donor_files:
        raise FileNotFoundError("Нет доступных donor JSON файлов.")
    return os.path.join(donor_folder, random.choice(donor_files))


async def process_account(account_folder):
    global successful, failed
    session_path = None
    new_json_path = None

    # print(f"[ИНФО] Обрабатывается аккаунт: {account_folder}")
    try:
        tdata_path = os.path.join(base_folder, account_folder, "tdata")
        if not os.path.exists(tdata_path):
            print(f"[ОШИБКА] Папка {account_folder} не найдена")
            failed += 1
            return False

        try:
            tdesk = TDesktop(tdata_path)
        except OpenTeleException:
            print(f"[ОШИБКА] Не удалось загрузить tdata {account_folder}")
            failed += 1
            return False
        except Exception as e:
            print(f"[ОШИБКА] Ошибка загрузки tdata {account_folder}: {str(e)}")
            failed += 1
            return False

        if not tdesk.isLoaded():
            print(f"[ОШИБКА] Папка {account_folder} не загружена")
            failed += 1
            return False

        session_path = os.path.join(converted_folder, f"{account_folder}.session")
        try:
            client = await asyncio.wait_for(
                tdesk.ToTelethon(session=session_path, flag=UseCurrentSession),
                timeout=10,
            )
            await asyncio.wait_for(client.connect(), timeout=10)
            await client.disconnect()
        except asyncio.TimeoutError:
            print(f"[ОШИБКА] Таймаут при обработке {account_folder}")
            if os.path.exists(session_path):
                os.remove(session_path)
            failed += 1
            return False
        except Exception as e:
            print(f"[ОШИБКА] Ошибка при обработке {account_folder}: {str(e)}")
            if os.path.exists(session_path):
                os.remove(session_path)
            failed += 1
            return False

        try:
            donor_json_path = get_random_donor_json()
            new_json_path = os.path.join(converted_folder, f"{account_folder}.json")
            shutil.copy(donor_json_path, new_json_path)
            print(f"[УСПЕШНО] Аккаунт {account_folder} обработан")
            successful += 1
            return True
        except Exception as e:
            print(
                f"[ОШИБКА] Не удалось скопировать donor JSON для {account_folder}: {str(e)}"
            )
            if os.path.exists(session_path):
                os.remove(session_path)
            failed += 1
            return False

    except Exception as e:
        print(
            f"[ОШИБКА] Непредвиденная ошибка при обработке {account_folder}: {str(e)}"
        )
        if session_path and os.path.exists(session_path):
            os.remove(session_path)
        if new_json_path and os.path.exists(new_json_path):
            os.remove(new_json_path)
        failed += 1
        return False


async def main():
    os.makedirs(converted_folder, exist_ok=True)
    accounts = [
        d
        for d in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, d))
    ]

    if not accounts:
        print("[ОШИБКА] Не найдено аккаунтов для обработки")
        return

    results = await asyncio.gather(
        *(process_account(account) for account in accounts), return_exceptions=True
    )

    print(f"\nУспешно обработано: {successful}")
    print(f"Не удалось обработать: {failed}")
    print(f"Всего аккаунтов: {len(accounts)}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\nУспешно обработано: {successful}")
        print(f"Не удалось обработать: {failed}")
        print("\nПрограмма остановлена пользователем")
    except Exception as e:
        print(f"\nПрограмма завершилась с ошибкой: {str(e)}")
