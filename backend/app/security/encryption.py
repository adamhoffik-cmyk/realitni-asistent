"""AES-256-GCM šifrování pro OAuth tokeny + klientské PII.

Klíč se čte z env `PII_ENCRYPTION_KEY` (base64 32B).
"""
from __future__ import annotations

import base64
import logging
from functools import lru_cache

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def _get_cipher() -> AESGCM:
    settings = get_settings()
    if not settings.pii_encryption_key:
        raise RuntimeError(
            "PII_ENCRYPTION_KEY není nastaven. Vygeneruj: "
            "python -c \"import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())\""
        )
    key = base64.b64decode(settings.pii_encryption_key)
    if len(key) != 32:
        raise RuntimeError(f"PII klíč má {len(key)} bajtů, očekávám 32")
    return AESGCM(key)


def encrypt(plaintext: str) -> bytes:
    """Zašifruje string → bytes (nonce 12B + ciphertext + auth tag)."""
    if not plaintext:
        return b""
    import os

    cipher = _get_cipher()
    nonce = os.urandom(12)
    ct = cipher.encrypt(nonce, plaintext.encode("utf-8"), associated_data=None)
    return nonce + ct


def decrypt(ciphertext: bytes) -> str:
    """Dešifruje bytes → string."""
    if not ciphertext:
        return ""
    cipher = _get_cipher()
    nonce = ciphertext[:12]
    ct = ciphertext[12:]
    return cipher.decrypt(nonce, ct, associated_data=None).decode("utf-8")
