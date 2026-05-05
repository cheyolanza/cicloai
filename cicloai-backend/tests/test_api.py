from fastapi.testclient import TestClient

from cicloai.interfaces.api import dependencies
from cicloai.interfaces.api.main import app


class FakeAdminUser:
    username = "admin"


class FakeAdminAuthService:
    def authenticate(self, username: str, password: str) -> FakeAdminUser | None:
        if username == "admin" and password == "secret":
            return FakeAdminUser()

        return None


def test_api_health_ingest_query(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    dependencies.settings.cache_clear()
    dependencies.document_repository.cache_clear()
    dependencies.vector_index.cache_clear()
    dependencies.chunker.cache_clear()

    client = TestClient(app)

    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"

    ingest_response = client.post(
        "/ingest",
        json={
            "text": "Las inscripciones masivas de CicloAI se procesan desde Excel y validan equipo unico.",
            "metadata": {"source": "api-test"},
        },
    )
    assert ingest_response.status_code == 200
    assert ingest_response.json()["chunks_indexed"] == 1

    query_response = client.post(
        "/query", json={"question": "Que valida el Excel masivo?"}
    )
    assert query_response.status_code == 200
    payload = query_response.json()
    assert payload["sources"]
    assert "CicloAI" in payload["answer"]


def test_recaptcha_verification_mock(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("RECAPTCHA_ENABLE_MOCKS", "true")
    dependencies.settings.cache_clear()
    dependencies.document_repository.cache_clear()
    dependencies.vector_index.cache_clear()
    dependencies.chunker.cache_clear()

    client = TestClient(app)

    response = client.post(
        "/api/v1/security/recaptcha/verify",
        json={"token": "widget-token", "action": "LOGIN"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert payload["score"] == 0.9
    assert payload["action"] == "LOGIN"


def test_admin_login_success_and_session(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("JWT_SECRET_KEY", "admin-api-test-secret")
    dependencies.settings.cache_clear()
    app.dependency_overrides[dependencies.admin_auth_service] = (
        lambda: FakeAdminAuthService()
    )

    try:
        client = TestClient(app)

        login_response = client.post(
            "/api/v1/admin/login", json={"username": "admin", "password": "secret"}
        )
        assert login_response.status_code == 200

        login_payload = login_response.json()
        assert login_payload["username"] == "admin"
        assert login_payload["token_type"] == "bearer"

        session_response = client.get(
            "/api/v1/admin/me",
            headers={"Authorization": f"Bearer {login_payload['access_token']}"},
        )
        assert session_response.status_code == 200
        assert session_response.json() == {"username": "admin"}
    finally:
        app.dependency_overrides.clear()


def test_admin_login_rejects_invalid_credentials(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path))
    dependencies.settings.cache_clear()
    app.dependency_overrides[dependencies.admin_auth_service] = (
        lambda: FakeAdminAuthService()
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/admin/login", json={"username": "admin", "password": "bad"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Username o password incorrectos."
    finally:
        app.dependency_overrides.clear()
