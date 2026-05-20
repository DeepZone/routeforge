from __future__ import annotations

import hashlib
import hmac
import os
import re


def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    digest = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"sha256${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        _, salt, digest = password_hash.split('$', 2)
    except ValueError:
        return False
    check = hashlib.sha256((salt + password).encode()).hexdigest()
    return hmac.compare_digest(check, digest)


def validate_password_strength(password: str) -> list[str]:
    errors: list[str] = []
    if not password or not password.strip():
        errors.append("Password must not be empty.")
        return errors
    if len(password) < 10:
        errors.append("Password must be at least 10 characters long.")
    if not re.search(r"[A-Za-z]", password):
        errors.append("Password must contain at least one letter.")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number.")
    return errors
