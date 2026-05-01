from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from cicloai.application.bike_race_service import BikeRaceService
from cicloai.application.bike_team_service import BikeTeamService
from cicloai.application.biker_lookup_action_service import BikerLookupActionService
from cicloai.application.biker_search_service import BikerSearchService
from cicloai.application.admin_auth_service import AdminAuthService
from cicloai.application.admin_service import AdminService
from cicloai.application.captcha_service import CaptchaService
from cicloai.application.chunking import TextChunker
from cicloai.application.health_service import HealthService
from cicloai.application.ingest_service import IngestService
from cicloai.application.intent_detection_service import IntentDetectionService
from cicloai.application.query_service import QueryService
from cicloai.application.recaptcha_service import RecaptchaVerificationService
from cicloai.application.payment_proof_ocr_service import PaymentProofOcrService
from cicloai.application.payment_validation_service import PaymentValidationService
from cicloai.application.registration_service import RegistrationService
from cicloai.application.cycling_team_service import CyclingTeamService
from cicloai.application.token_service import TokenPayload, TokenService
from cicloai.infrastructure.config import Settings, get_settings
from cicloai.infrastructure.database.session import SessionLocal
from cicloai.infrastructure.llm.extractive_llm import ExtractiveLLMClient
from cicloai.infrastructure.repositories.json_document_repository import JsonDocumentRepository
from cicloai.infrastructure.vector_store.hash_vector_store import HashVectorStore
from cicloai.rag.config import build_rag_config
from cicloai.rag.prompt_builder import PromptBuilder
from cicloai.rag.rag_service import RagService
from cicloai.rag.retriever import Retriever
from cicloai.rag.vector_store import VectorStore

bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def settings() -> Settings:
    return get_settings()


@lru_cache
def document_repository() -> JsonDocumentRepository:
    storage_dir = settings().storage_dir
    return JsonDocumentRepository(storage_dir / "documents.json")


@lru_cache
def vector_index() -> HashVectorStore:
    config = settings()
    return HashVectorStore(config.storage_dir / "vectors.json", dimensions=config.vector_dimensions)


@lru_cache
def chunker() -> TextChunker:
    config = settings()
    return TextChunker(chunk_size=config.chunk_size, overlap=config.chunk_overlap)


def ingest_service() -> IngestService:
    return IngestService(document_repository(), vector_index(), chunker())


def query_service() -> QueryService:
    return QueryService(vector_index(), ExtractiveLLMClient(), default_top_k=settings().top_k)


def health_service() -> HealthService:
    return HealthService(document_repository(), vector_index())


def recaptcha_service() -> RecaptchaVerificationService:
    return RecaptchaVerificationService(settings())


def captcha_service() -> CaptchaService:
    return CaptchaService(settings())


def token_service() -> TokenService:
    return TokenService(settings())


def intent_detection_service() -> IntentDetectionService:
    return IntentDetectionService()


def rag_service() -> RagService:
    config = build_rag_config(settings())
    vector_store = VectorStore(config)
    return RagService(config, Retriever(vector_store, config), PromptBuilder())


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def bike_race_service(db: Session = Depends(get_db)) -> BikeRaceService:
    return BikeRaceService(db)


def admin_auth_service(db: Session = Depends(get_db)) -> AdminAuthService:
    return AdminAuthService(db)


def admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(db)


def bike_team_service(db: Session = Depends(get_db)) -> BikeTeamService:
    return BikeTeamService(db)


def cycling_team_service(db: Session = Depends(get_db)) -> CyclingTeamService:
    return CyclingTeamService(db)


def biker_search_service(db: Session = Depends(get_db)) -> BikerSearchService:
    return BikerSearchService(db)


def biker_lookup_action_service(
    db: Session = Depends(get_db),
    teams: CyclingTeamService = Depends(cycling_team_service),
) -> BikerLookupActionService:
    return BikerLookupActionService(db, teams)


def payment_ocr_service() -> PaymentProofOcrService:
    return PaymentProofOcrService(settings())


def payment_validation_service(db: Session = Depends(get_db)) -> PaymentValidationService:
    return PaymentValidationService(db)


def registration_service(
    db: Session = Depends(get_db),
    payment_ocr: PaymentProofOcrService = Depends(payment_ocr_service),
    payment_validator: PaymentValidationService = Depends(payment_validation_service),
) -> RegistrationService:
    return RegistrationService(db, payment_ocr, payment_validator)


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    service: TokenService = Depends(token_service),
) -> TokenPayload:
    if credentials is None or credentials.scheme.lower() != "bearer":
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Operación no permitida. El usuario debe validarse.")

    try:
        return service.decode_public_user_token(credentials.credentials)
    except InvalidTokenError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Operación no permitida. El usuario debe validarse.") from exc


def get_current_admin_from_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    service: TokenService = Depends(token_service),
) -> TokenPayload:
    if credentials is None or credentials.scheme.lower() != "bearer":
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Credenciales de administrador requeridas.")

    try:
        return service.decode_admin_user_token(credentials.credentials)
    except InvalidTokenError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Sesión de administrador inválida o expirada.") from exc
