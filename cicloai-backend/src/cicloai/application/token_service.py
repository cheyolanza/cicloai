from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict

import jwt
from jwt import InvalidTokenError

from cicloai.infrastructure.config import Settings


class TokenPayload(TypedDict):
    sub: str
    scope: str
    iat: int
    exp: int
    token_type: str


class TokenService:
    """Issues and validates public Bearer tokens after CAPTCHA verification."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_public_user_token(self) -> tuple[str, int]:
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(seconds=self._settings.jwt_expire_seconds)
        payload = {
            "sub": "captcha_validated_user",
            "scope": "public_user",
            "iat": int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp()),
            "token_type": "bearer",
        }
        token = jwt.encode(payload, self._settings.jwt_secret_key, algorithm=self._settings.jwt_algorithm)
        return token, self._settings.jwt_expire_seconds

    def create_admin_user_token(self, username: str) -> tuple[str, int]:
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(seconds=self._settings.jwt_expire_seconds)
        payload = {
            "sub": username,
            "scope": "admin_user",
            "iat": int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp()),
            "token_type": "bearer",
        }
        token = jwt.encode(payload, self._settings.jwt_secret_key, algorithm=self._settings.jwt_algorithm)
        return token, self._settings.jwt_expire_seconds

    def decode_public_user_token(self, token: str) -> TokenPayload:
        payload = jwt.decode(token, self._settings.jwt_secret_key, algorithms=[self._settings.jwt_algorithm])

        if payload.get("token_type") != "bearer" or payload.get("scope") != "public_user":
            raise InvalidTokenError("Invalid token claims")

        return {
            "sub": str(payload["sub"]),
            "scope": str(payload["scope"]),
            "iat": int(payload["iat"]),
            "exp": int(payload["exp"]),
            "token_type": str(payload["token_type"]),
        }

    def decode_admin_user_token(self, token: str) -> TokenPayload:
        payload = jwt.decode(token, self._settings.jwt_secret_key, algorithms=[self._settings.jwt_algorithm])

        if payload.get("token_type") != "bearer" or payload.get("scope") != "admin_user":
            raise InvalidTokenError("Invalid token claims")

        return {
            "sub": str(payload["sub"]),
            "scope": str(payload["scope"]),
            "iat": int(payload["iat"]),
            "exp": int(payload["exp"]),
            "token_type": str(payload["token_type"]),
        }

    def create_registration_review_token(self, review_payload: dict[str, Any]) -> str:
        """Signs a Human-in-the-Loop review snapshot without inserting it yet.

        The frontend sends this opaque token back only after the user confirms
        the agent summary. This keeps the backend stateless for pending reviews
        and avoids trusting editable browser state at final registration time.
        """

        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(seconds=self._settings.jwt_expire_seconds)
        payload = {
            "sub": "registration_review",
            "scope": "registration_review",
            "iat": int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp()),
            "token_type": "review",
            "review": review_payload,
        }
        return jwt.encode(payload, self._settings.jwt_secret_key, algorithm=self._settings.jwt_algorithm)

    def decode_registration_review_token(self, token: str) -> dict[str, Any]:
        payload = jwt.decode(token, self._settings.jwt_secret_key, algorithms=[self._settings.jwt_algorithm])

        if payload.get("token_type") != "review" or payload.get("scope") != "registration_review":
            raise InvalidTokenError("Invalid review token claims")

        review = payload.get("review")
        if not isinstance(review, dict):
            raise InvalidTokenError("Invalid review payload")

        return review
