from cicloai.infrastructure.config import build_database_url, parse_cors_allowed_origins


def test_build_database_url_prefers_explicit_database_url(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("DB_HOST", "ignored")

    assert build_database_url() == "sqlite:///./test.db"


def test_build_database_url_from_local_db_parts(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("CLOUD_SQL_INSTANCE_CONNECTION_NAME", raising=False)
    monkeypatch.setenv("DB_HOST", "postgres")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "cicloai")
    monkeypatch.setenv("DB_USER", "cicloai_user")
    monkeypatch.setenv("DB_PASSWORD", "local-password")

    assert (
        build_database_url()
        == "postgresql+psycopg2://cicloai_user:local-password@postgres:5432/cicloai"
    )


def test_build_database_url_from_cloud_sql_socket(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_NAME", "cicloai")
    monkeypatch.setenv("DB_USER", "cicloai_user")
    monkeypatch.setenv("DB_PASSWORD", "cloud-password")
    monkeypatch.setenv(
        "CLOUD_SQL_INSTANCE_CONNECTION_NAME", "ciclo-ai:us-central1:cicloai-postgres"
    )

    assert build_database_url() == (
        "postgresql+psycopg2://cicloai_user:cloud-password@/cicloai"
        "?host=/cloudsql/ciclo-ai:us-central1:cicloai-postgres"
    )


def test_parse_cors_allowed_origins_trims_and_normalizes_trailing_slashes() -> None:
    origins = parse_cors_allowed_origins(
        "http://localhost:5173, https://cicloai-frontend-674379443086.us-central1.run.app/, https://cicloai.com"
    )

    assert origins == (
        "http://localhost:5173",
        "https://cicloai-frontend-674379443086.us-central1.run.app",
        "https://cicloai.com",
    )


def test_parse_cors_allowed_origins_uses_local_fallback() -> None:
    assert parse_cors_allowed_origins("") == (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://cicloai-frontend-674379443086.us-central1.run.app",
        "https://cicloai.com",
        "https://www.cicloai.com",
    )
