from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Tuple

PBKDF2_ITERATIONS = 390000
TOKEN_BYTES = 32


def generate_salt(length: int = 16) -> bytes:
    return os.urandom(length)


def hash_password(password: str, salt: bytes) -> bytes:
    if not isinstance(password, str):
        raise TypeError("password must be a string")
    if not isinstance(salt, (bytes, bytearray)):
        raise TypeError("salt must be bytes")
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)


def create_password_digest(password: str) -> Tuple[bytes, bytes]:
    salt = generate_salt()
    digest = hash_password(password, salt)
    return salt, digest


def verify_password(password: str, salt: bytes, digest: bytes) -> bool:
    calculated = hash_password(password, salt)
    return hmac.compare_digest(calculated, digest)


def create_access_token() -> str:
    return secrets.token_urlsafe(TOKEN_BYTES)


def token_expiry(days: int = 7) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(days=days)
