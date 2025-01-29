import os

from config import LOGS_DIR


def write_to_file(filename, data):
    try:
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        with open(filename, "a", encoding="utf-8") as f:
            f.write(data + "\n")
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")


def parse_proxy(proxy_line):
    try:
        user_password, host_port = proxy_line.rsplit("@", 1)
        user, password = user_password.split(":", 1)
        host, port = host_port.split(":", 1)
        return {
            "scheme": "http",
            "hostname": host,
            "port": int(port),
            "username": user,
            "password": password,
        }
    except Exception as e:
        print(f"Ошибка при парсинге прокси: {e}")
        return None
