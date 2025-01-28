from config import DATA_FILES_DIR


def get_bip39_words():
    with open(f"{DATA_FILES_DIR}/bip39_words.txt", "r") as f:
        BIP39_WORDS = set(word.strip() for word in f.readlines())
    return BIP39_WORDS


def get_usernames():
    with open(f"{DATA_FILES_DIR}/usernames.txt", "r") as f:
        USERNAMES = set(line.strip() for line in f)
    return USERNAMES


def get_proxies():
    with open(f"{DATA_FILES_DIR}/proxy.txt", "r") as f:
        PROXIES = [line.strip() for line in f if line.strip()]
    return PROXIES
