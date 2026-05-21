import base64
from cryptography.fernet import Fernet

from app.config import settings


def _get_fernet() -> Fernet:
    key = settings.encryption_key
    # Ensure key is valid Fernet key (URL-safe base64, 32 bytes)
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception:
        # If key isn't valid Fernet format, derive one
        padded = (key + "=" * (44 - len(key) % 44))[:44]
        return Fernet(padded.encode())


def encrypt(value: str) -> str:
    f = _get_fernet()
    return f.encrypt(value.encode()).decode()


def decrypt(token: str) -> str:
    f = _get_fernet()
    return f.decrypt(token.encode()).decode()
