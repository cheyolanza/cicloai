from fastapi.testclient import TestClient

from cicloai.interfaces.api import dependencies
from cicloai.interfaces.api.main import app


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

    query_response = client.post("/query", json={"question": "Que valida el Excel masivo?"})
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
