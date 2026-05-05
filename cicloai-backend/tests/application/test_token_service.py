from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from jwt import ExpiredSignatureError, InvalidTokenError

from cicloai.application.token_service import TokenService
from cicloai.infrastructure.config import Settings


def settings(*, secret: str = "test-secret", expires: int = 600) -> Settings:
    return Settings(
        jwt_secret_key=secret,
        jwt_algorithm="HS256",
        jwt_expire_seconds=expires,
    )


def service(*, secret: str = "test-secret", expires: int = 600) -> TokenService:
    return TokenService(settings(secret=secret, expires=expires))


def encode(claims: dict, *, secret: str = "test-secret") -> str:
    return jwt.encode(claims, secret, algorithm="HS256")


def valid_claims(**overrides) -> dict:
    now = datetime.now(timezone.utc)
    claims = {
        "sub": "captcha_validated_user",
        "scope": "public_user",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=10)).timestamp()),
        "token_type": "bearer",
    }
    claims.update(overrides)
    return claims


def test_public_and_admin_tokens_are_valid_bearer_tokens() -> None:
    token_service = service(expires=900)

    public_token, public_ttl = token_service.create_public_user_token()
    admin_token, admin_ttl = token_service.create_admin_user_token("admin")

    assert public_ttl == admin_ttl == 900
    assert (
        token_service.decode_public_user_token(public_token)["scope"] == "public_user"
    )
    admin_payload = token_service.decode_admin_user_token(admin_token)
    assert admin_payload["sub"] == "admin"
    assert admin_payload["scope"] == "admin_user"


def test_decode_rejects_invalid_public_claims_and_invalid_admin_claims() -> None:
    token_service = service()

    with pytest.raises(InvalidTokenError, match="Invalid token claims"):
        token_service.decode_public_user_token(encode(valid_claims(scope="admin_user")))

    with pytest.raises(InvalidTokenError, match="Invalid token claims"):
        token_service.decode_admin_user_token(encode(valid_claims()))


def test_decode_rejects_expired_and_malformed_tokens() -> None:
    token_service = service()
    now = datetime.now(timezone.utc)
    expired = encode(
        valid_claims(
            iat=int((now - timedelta(hours=2)).timestamp()),
            exp=int((now - timedelta(hours=1)).timestamp()),
        )
    )

    with pytest.raises(ExpiredSignatureError):
        token_service.decode_public_user_token(expired)
    with pytest.raises(InvalidTokenError):
        token_service.decode_public_user_token("not-a-jwt")


def test_registration_review_token_round_trips_dict_payload() -> None:
    payload = {"dni": "1234567", "payment": {"status": "validated"}}
    token = service().create_registration_review_token(payload)

    assert service().decode_registration_review_token(token) == payload


@pytest.mark.parametrize("review", [None, "text", ["list"]])
def test_registration_review_token_rejects_non_dict_review(review) -> None:
    token = encode(
        valid_claims(scope="registration_review", token_type="review", review=review)
    )

    with pytest.raises(InvalidTokenError, match="Invalid review payload"):
        service().decode_registration_review_token(token)


def test_registration_review_token_rejects_wrong_claims() -> None:
    token = encode(valid_claims(scope="public_user", token_type="bearer", review={}))

    with pytest.raises(InvalidTokenError, match="Invalid review token claims"):
        service().decode_registration_review_token(token)
