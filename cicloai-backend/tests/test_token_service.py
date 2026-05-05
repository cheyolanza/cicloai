from datetime import datetime, timedelta, timezone

import jwt
import pytest
from jwt import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError

from cicloai.application.token_service import TokenService
from cicloai.infrastructure.config import Settings


def build_settings(
    *, secret: str = "unit-test-secret", expires_in: int = 3600
) -> Settings:
    return Settings(
        jwt_secret_key=secret, jwt_algorithm="HS256", jwt_expire_seconds=expires_in
    )


def build_service(
    *, secret: str = "unit-test-secret", expires_in: int = 3600
) -> TokenService:
    return TokenService(build_settings(secret=secret, expires_in=expires_in))


def encode_payload(payload: dict, *, secret: str = "unit-test-secret") -> str:
    return jwt.encode(payload, secret, algorithm="HS256")


def test_create_public_user_token_returns_bearer_token_and_expiration() -> None:
    service = build_service(expires_in=900)

    token, expires_in = service.create_public_user_token()
    payload = service.decode_public_user_token(token)

    assert expires_in == 900
    assert payload["sub"] == "captcha_validated_user"
    assert payload["scope"] == "public_user"
    assert payload["token_type"] == "bearer"
    assert payload["exp"] - payload["iat"] == 900


def test_create_admin_user_token_returns_bearer_token_and_expiration() -> None:
    service = build_service(expires_in=900)

    token, expires_in = service.create_admin_user_token("admin")
    payload = service.decode_admin_user_token(token)

    assert expires_in == 900
    assert payload["sub"] == "admin"
    assert payload["scope"] == "admin_user"
    assert payload["token_type"] == "bearer"
    assert payload["exp"] - payload["iat"] == 900


def test_decode_public_user_token_casts_numeric_claims_to_int() -> None:
    service = build_service()
    issued_at = int(datetime.now(timezone.utc).timestamp())
    token = encode_payload(
        {
            "sub": "captcha_validated_user",
            "scope": "public_user",
            "iat": str(issued_at),
            "exp": str(issued_at + 3600),
            "token_type": "bearer",
        }
    )

    payload = service.decode_public_user_token(token)

    assert payload == {
        "sub": "captcha_validated_user",
        "scope": "public_user",
        "iat": issued_at,
        "exp": issued_at + 3600,
        "token_type": "bearer",
    }


@pytest.mark.parametrize(
    "claims_override",
    [
        {"token_type": "review"},
        {"scope": "registration_review"},
    ],
)
def test_decode_public_user_token_rejects_invalid_claims(claims_override: dict) -> None:
    service = build_service()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "captcha_validated_user",
        "scope": "public_user",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "token_type": "bearer",
    }
    payload.update(claims_override)

    with pytest.raises(InvalidTokenError, match="Invalid token claims"):
        service.decode_public_user_token(encode_payload(payload))


def test_decode_admin_user_token_rejects_public_token() -> None:
    service = build_service()
    public_token, _expires_in = service.create_public_user_token()

    with pytest.raises(InvalidTokenError, match="Invalid token claims"):
        service.decode_admin_user_token(public_token)


def test_decode_public_user_token_rejects_wrong_signature() -> None:
    service = build_service(secret="expected-secret")
    token, _expires_in = build_service(secret="other-secret").create_public_user_token()

    with pytest.raises(InvalidSignatureError):
        service.decode_public_user_token(token)


def test_decode_public_user_token_rejects_expired_token() -> None:
    service = build_service()
    now = datetime.now(timezone.utc)
    token = encode_payload(
        {
            "sub": "captcha_validated_user",
            "scope": "public_user",
            "iat": int((now - timedelta(hours=2)).timestamp()),
            "exp": int((now - timedelta(hours=1)).timestamp()),
            "token_type": "bearer",
        }
    )

    with pytest.raises(ExpiredSignatureError):
        service.decode_public_user_token(token)


def test_create_registration_review_token_round_trips_review_payload() -> None:
    service = build_service(expires_in=600)
    review_payload = {
        "full_name": "Juan Perez",
        "dni": "1234567",
        "detected_category": "Federado Master A2",
        "payment": {"status": "approved", "transaction_id": "1234567890"},
    }

    token = service.create_registration_review_token(review_payload)
    decoded_review = service.decode_registration_review_token(token)

    assert decoded_review == review_payload


def test_decode_registration_review_token_rejects_public_token() -> None:
    service = build_service()
    public_token, _expires_in = service.create_public_user_token()

    with pytest.raises(InvalidTokenError, match="Invalid review token claims"):
        service.decode_registration_review_token(public_token)


def test_decode_registration_review_token_rejects_missing_review_payload() -> None:
    service = build_service()
    now = datetime.now(timezone.utc)
    token = encode_payload(
        {
            "sub": "registration_review",
            "scope": "registration_review",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "token_type": "review",
        }
    )

    with pytest.raises(InvalidTokenError, match="Invalid review payload"):
        service.decode_registration_review_token(token)


@pytest.mark.parametrize("review_value", [None, "not-a-dict", ["list"]])
def test_decode_registration_review_token_rejects_non_dict_review_payload(
    review_value,
) -> None:
    service = build_service()
    now = datetime.now(timezone.utc)
    token = encode_payload(
        {
            "sub": "registration_review",
            "scope": "registration_review",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "token_type": "review",
            "review": review_value,
        }
    )

    with pytest.raises(InvalidTokenError, match="Invalid review payload"):
        service.decode_registration_review_token(token)
