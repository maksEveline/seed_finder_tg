import re

HASH_PATTERN = re.compile(r"0x[a-z0-9]{64}")
BITCOIN_PATTERN = re.compile(r"\b[a-zA-Z0-9]{52}\b")
SOLANA_PATTERN = re.compile(
    r"\b[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{88}\b"
)
TRON_PATTERN = re.compile(r"\b4[1234567890abcdef]{63}\b")
WIF_PATTERN = re.compile(r"\b[5KL][1-9A-HJ-NP-Za-km-z]{50,51}\b")
