import re

HASH_PATTERN = re.compile(r"0x[a-z-0-9]{64}")
BITCOIN_PATTERN = re.compile(
    r"\b[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{44}\d{8}\b"
)
SOLANA_PATTERN = re.compile(
    r"\b[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{87}\b"
)
TRON_PATTERN = re.compile(r"\b4[1234567890abcdef]{63}\b")
