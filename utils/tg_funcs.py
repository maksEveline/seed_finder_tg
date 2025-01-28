import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_message_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
    if response.status_code != 200:
        print(f"Ошибка отправки сообщения: {response.text}")
