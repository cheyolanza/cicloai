from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from cicloai.infrastructure.models.user import User

PASSWORD_PREFIX = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 260000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    encoded_salt = base64.b64encode(salt).decode("ascii")
    encoded_digest = base64.b64encode(digest).decode("ascii")
    return f"{PASSWORD_PREFIX}${PASSWORD_ITERATIONS}${encoded_salt}${encoded_digest}"


def verify_password(password: str, stored_password: str) -> bool:
    parts = stored_password.split("$")
    if len(parts) != 4 or parts[0] != PASSWORD_PREFIX:
        return hmac.compare_digest(password, stored_password)

    _prefix, raw_iterations, encoded_salt, encoded_digest = parts
    try:
        iterations = int(raw_iterations)
        salt = base64.b64decode(encoded_salt.encode("ascii"), validate=True)
        expected_digest = base64.b64decode(encoded_digest.encode("ascii"), validate=True)
    except (ValueError, TypeError):
        return False

    actual_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual_digest, expected_digest)


class AdminAuthService:
    """Validates admin credentials against the users table."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def authenticate(self, username: str, password: str) -> User | None:
        statement = select(User).where(User.username == username.strip())
        user = self._db.execute(statement).scalar_one_or_none()

        if user is None or not verify_password(password, user.password):
            return None

        return user
