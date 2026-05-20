from __future__ import annotations

import hashlib
import hmac
import os
import re

PBKDF2_ITERATIONS = 210_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, *parts = password_hash.split('$')
    except ValueError:
        return False

    if scheme == "pbkdf2_sha256" and len(parts) == 3:
        iterations_s, salt_hex, digest = parts
        try:
            iterations = int(iterations_s)
            salt = bytes.fromhex(salt_hex)
        except ValueError:
            return False
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations).hex()
        return hmac.compare_digest(check, digest)

    if scheme == "sha256" and len(parts) == 2:
        salt, digest = parts
        check = hashlib.sha256((salt + password).encode()).hexdigest()
        return hmac.compare_digest(check, digest)

    return False


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
