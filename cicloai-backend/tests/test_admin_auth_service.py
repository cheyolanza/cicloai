from cicloai.application.admin_auth_service import hash_password, verify_password


def test_verify_password_accepts_hashed_password() -> None:
    stored_password = hash_password("secret-password")

    assert verify_password("secret-password", stored_password) is True
    assert verify_password("wrong-password", stored_password) is False


def test_verify_password_accepts_plain_stored_password_for_existing_rows() -> None:
    assert verify_password("admin123", "admin123") is True
    assert verify_password("other", "admin123") is False
