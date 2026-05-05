from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus


DEFAULT_CORS_ALLOWED_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://cicloai-frontend-674379443086.us-central1.run.app",
    "https://cicloai.com",
    "https://www.cicloai.com",
)


@dataclass(frozen=True)
class Settings:
    app_name: str = "CicloAI Backend"
    environment: str = "local"
    storage_dir: Path = Path("data")
    chunk_size: int = 120
    chunk_overlap: int = 25
    top_k: int = 3
    vector_dimensions: int = 384
    database_url: str = (
        "postgresql+psycopg2://cicloai_user:cicloai_pass@localhost:5432/cicloai-db"
    )
    jwt_secret_key: str = "change-me-local-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_seconds: int = 3600
    google_recaptcha_secret_key: str = ""
    enable_captcha_mock: bool = True
    recaptcha_project_id: str = "ciclo-ai"
    recaptcha_site_key: str = "6LcYJMcsAAAAANnSzsP1VP4bJ86DKcGQzhVbZNO2"
    recaptcha_min_score: float = 0.5
    recaptcha_enable_mocks: bool = True
    category_rules_pdf_path: Path = Path(
        "assets/documents/category_rules/convocatoria.txt"
    )
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.70
    rag_documents_dir: Path = Path("assets/documents/category_rules")
    rag_vector_store_dir: Path = Path("storage/vector_store")
    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 150
    rag_auto_index: bool = False
    enable_rag_mock: bool = False
    google_application_credentials: str = ""
    google_cloud_project_id: str = "ciclo-ai"
    enable_ocr_mock: bool = True
    google_vision_ocr_endpoint: str = "https://vision.googleapis.com/v1/images:annotate"
    payment_proofs_storage_dir: Path = Path("assets/payments")
    cors_allowed_origins: tuple[str, ...] = DEFAULT_CORS_ALLOWED_ORIGINS


def build_database_url() -> str:
    """Builds the SQLAlchemy URL from environment variables when needed.

    `DATABASE_URL` remains the highest-priority override. Cloud Run can instead
    provide discrete DB variables plus `CLOUD_SQL_INSTANCE_CONNECTION_NAME`,
    which makes local Docker, CI and Cloud SQL deployment share one settings
    boundary without hardcoding credentials in code.
    """

    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    db_user = os.getenv("DB_USER", "cicloai_user")
    db_password = os.getenv("DB_PASSWORD", "cicloai_pass_DB1")
    db_name = os.getenv("DB_NAME", "cicloai-db")
    cloud_sql_connection_name = os.getenv(
        "CLOUD_SQL_INSTANCE_CONNECTION_NAME", ""
    ).strip()

    encoded_user = quote_plus(db_user)
    encoded_password = quote_plus(db_password)
    encoded_db_name = quote_plus(db_name)

    if cloud_sql_connection_name:
        return (
            f"postgresql+psycopg2://{encoded_user}:{encoded_password}@/{encoded_db_name}"
            f"?host=/cloudsql/{cloud_sql_connection_name}"
        )

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    return f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{db_host}:{db_port}/{encoded_db_name}"


def parse_cors_allowed_origins(raw_value: str | None) -> tuple[str, ...]:
    """Parses comma-separated CORS origins from environment configuration.

    CORS is deployment-specific: local development, Cloud Run preview URLs and
    custom domains should be configured outside code. The fallback keeps the
    developer experience working when no env var is provided.
    """

    if not raw_value:
        return DEFAULT_CORS_ALLOWED_ORIGINS

    origins = tuple(
        origin.strip().rstrip("/") for origin in raw_value.split(",") if origin.strip()
    )
    return origins or DEFAULT_CORS_ALLOWED_ORIGINS


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "CicloAI Backend"),
        environment=os.getenv("ENVIRONMENT", "local"),
        storage_dir=Path(os.getenv("STORAGE_DIR", "data")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "120")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "25")),
        top_k=int(os.getenv("TOP_K", "3")),
        vector_dimensions=int(os.getenv("VECTOR_DIMENSIONS", "384")),
        database_url=build_database_url(),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", "change-me-local-secret"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_expire_seconds=int(os.getenv("JWT_EXPIRE_SECONDS", "3600")),
        google_recaptcha_secret_key=os.getenv("GOOGLE_RECAPTCHA_SECRET_KEY", ""),
        enable_captcha_mock=os.getenv("ENABLE_CAPTCHA_MOCK", "true").lower() == "true",
        recaptcha_project_id=os.getenv("RECAPTCHA_PROJECT_ID", "ciclo-ai"),
        recaptcha_site_key=os.getenv(
            "RECAPTCHA_SITE_KEY", "6LcYJMcsAAAAANnSzsP1VP4bJ86DKcGQzhVbZNO2"
        ),
        recaptcha_min_score=float(os.getenv("RECAPTCHA_MIN_SCORE", "0.5")),
        recaptcha_enable_mocks=os.getenv("RECAPTCHA_ENABLE_MOCKS", "true").lower()
        == "true",
        category_rules_pdf_path=Path(
            os.getenv(
                "CATEGORY_RULES_PDF_PATH",
                "assets/documents/category_rules/convocatoria.txt",
            )
        ),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_embedding_model=os.getenv(
            "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
        ),
        rag_top_k=int(os.getenv("RAG_TOP_K", "5")),
        rag_similarity_threshold=float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.70")),
        rag_documents_dir=Path(
            os.getenv("RAG_DOCUMENTS_DIR", "assets/documents/category_rules")
        ),
        rag_vector_store_dir=Path(
            os.getenv("RAG_VECTOR_STORE_DIR", "storage/vector_store")
        ),
        rag_chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "800")),
        rag_chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "150")),
        rag_auto_index=os.getenv("RAG_AUTO_INDEX", "false").lower() == "true",
        enable_rag_mock=os.getenv("ENABLE_RAG_MOCK", "false").lower() == "true",
        google_application_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
        google_cloud_project_id=os.getenv("GOOGLE_CLOUD_PROJECT_ID", "ciclo-ai"),
        enable_ocr_mock=os.getenv("ENABLE_OCR_MOCK", "true").lower() == "true",
        google_vision_ocr_endpoint=os.getenv(
            "GOOGLE_VISION_OCR_ENDPOINT",
            "https://vision.googleapis.com/v1/images:annotate",
        ),
        payment_proofs_storage_dir=Path(
            os.getenv("PAYMENT_PROOFS_STORAGE_DIR", "assets/payments")
        ),
        cors_allowed_origins=parse_cors_allowed_origins(
            os.getenv("CORS_ALLOWED_ORIGINS")
        ),
    )
