from __future__ import annotations

import base64
import logging
from datetime import date
from io import StringIO
from pathlib import Path
from uuid import uuid4
from uuid import UUID

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from jwt import InvalidTokenError

from cicloai.application.health_service import HealthService
from cicloai.application.ingest_service import IngestService
from cicloai.application.intent_detection_service import IntentDetectionService
from cicloai.application.query_service import QueryService
from cicloai.application.recaptcha_service import RecaptchaVerificationService
from cicloai.application.registration_service import NewBikerRegistrationInput, RegistrationReview, RegistrationService
from cicloai.application.google_vision_ocr_service import (
    GoogleVisionOcrConfigurationError,
    GoogleVisionOcrProcessingError,
)
from cicloai.application.biker_lookup_action_service import BikerLookupActionService
from cicloai.application.biker_search_service import BikerSearchService
from cicloai.application.bike_race_service import BikeRaceService
from cicloai.application.bike_team_service import BikeTeamService
from cicloai.application.captcha_service import CaptchaService
from cicloai.application.cycling_team_service import CyclingTeamService
from cicloai.application.token_service import TokenPayload, TokenService
from cicloai.interfaces.api.dependencies import (
    bike_race_service,
    bike_team_service,
    biker_lookup_action_service,
    biker_search_service,
    captcha_service,
    cycling_team_service,
    get_current_user_from_token,
    health_service,
    ingest_service,
    intent_detection_service,
    query_service,
    recaptcha_service,
    registration_service,
    rag_service,
    settings,
    token_service,
)
from cicloai.interfaces.api.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    AgentChatSourceResponse,
    AgentChatUiActionResponse,
    BikeRaceResponse,
    BikeTeamResponse,
    BikerLookupActionRequest,
    BikerLookupActionResponse,
    BikerLookupActionBikerResponse,
    BikerSearchFoundResponse,
    BikerSearchNotFoundResponse,
    BikerSearchResultResponse,
    BulkRegistrationResponse,
    CaptchaVerifyRequest,
    CyclingTeamResponse,
    IngestRequest,
    IngestResponse,
    LastRegisteredRaceResponse,
    NoActiveRaceResponse,
    QueryRequest,
    QueryResponse,
    RecaptchaVerifyRequest,
    RecaptchaVerifyResponse,
    RegistrationConfirmRequest,
    RegistrationConfirmResponse,
    RegistrationReviewResponse,
    SourceResponse,
    TokenResponse,
)
from cicloai.rag.rag_service import RagService
from cicloai.rag.document_loader import DocumentLoader
from cicloai.rag.text_splitter import TextSplitter
from cicloai.rag.config import build_rag_config
from cicloai.rag.vector_store import KnowledgeBaseNotIndexedError
from cicloai.rag.vector_store import VectorStore


SUPPORTED_PAYMENT_PROOF_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


logger = logging.getLogger(__name__)


app = FastAPI(title=settings().app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def auto_index_rag_documents() -> None:
    if not settings().rag_auto_index:
        return

    config = build_rag_config(settings())
    documents = DocumentLoader(config.documents_dir).load()
    chunks = TextSplitter(config.chunk_size, config.chunk_overlap).split(documents)
    VectorStore(config).rebuild(chunks)


@app.get("/health")
def health(service: HealthService = Depends(health_service)) -> dict:
    return service.check()


@app.post("/ingest", response_model=IngestResponse)
def ingest(payload: IngestRequest, service: IngestService = Depends(ingest_service)) -> dict:
    try:
        return service.ingest(text=payload.text, metadata=payload.metadata, document_id=payload.document_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest, service: QueryService = Depends(query_service)) -> QueryResponse:
    try:
        answer = service.query(question=payload.question, top_k=payload.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return QueryResponse(
        answer=answer.answer,
        model=answer.model,
        latency_ms=answer.latency_ms,
        sources=[
            SourceResponse(
                document_id=source.chunk.document_id,
                chunk_id=source.chunk.chunk_id,
                score=source.score,
                text=source.chunk.text,
                metadata=source.chunk.metadata,
            )
            for source in answer.sources
        ],
    )


@app.post("/api/v1/agent/chat", response_model=AgentChatResponse)
def agent_chat(
    payload: AgentChatRequest,
    intent_detector: IntentDetectionService = Depends(intent_detection_service),
    _current_user: TokenPayload = Depends(get_current_user_from_token),
) -> AgentChatResponse:
    intent = intent_detector.detect(payload.message)

    if intent == "start_single_registration":
        return AgentChatResponse(
            answer="Perfecto, iniciemos tu inscripción unitaria.",
            intent=intent,
            ui_action=AgentChatUiActionResponse(type="SHOW_SINGLE_REGISTRATION"),
        )

    if intent == "start_bulk_registration":
        return AgentChatResponse(
            answer="Perfecto, iniciemos la inscripción masiva de tu equipo.",
            intent=intent,
            ui_action=AgentChatUiActionResponse(type="SHOW_BULK_REGISTRATION"),
        )

    if not RagService.is_convocatoria_domain(payload.message):
        return AgentChatResponse(
            answer="No tengo información sobre eso. Solo puedo responder preguntas relacionadas con la convocatoria de la carrera.",
            intent="rag_answer",
            ui_action=AgentChatUiActionResponse(type="NONE"),
        )

    try:
        rag = rag_service()
        answer = rag.answer(payload.message)
    except KnowledgeBaseNotIndexedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return AgentChatResponse(
        answer=answer.answer,
        intent="rag_answer",
        sources=[
            AgentChatSourceResponse(source_file=source.source_file, chunk_id=source.chunk_id)
            for source in answer.sources
        ],
        ui_action=AgentChatUiActionResponse(type="NONE"),
    )


def verify_recaptcha_response(
    payload: RecaptchaVerifyRequest,
    service: RecaptchaVerificationService,
) -> RecaptchaVerifyResponse:
    try:
        assessment = service.verify(token=payload.token, expected_action=payload.action)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return RecaptchaVerifyResponse(
        valid=assessment.valid,
        score=assessment.score,
        action=assessment.action,
        reasons=assessment.reasons,
    )


@app.post("/api/v1/security/recaptcha/verify", response_model=RecaptchaVerifyResponse)
def verify_recaptcha_v1(
    payload: RecaptchaVerifyRequest,
    service: RecaptchaVerificationService = Depends(recaptcha_service),
) -> RecaptchaVerifyResponse:
    return verify_recaptcha_response(payload=payload, service=service)


@app.post("/security/recaptcha/verify", response_model=RecaptchaVerifyResponse)
def verify_recaptcha(
    payload: RecaptchaVerifyRequest,
    service: RecaptchaVerificationService = Depends(recaptcha_service),
) -> RecaptchaVerifyResponse:
    return verify_recaptcha_response(payload=payload, service=service)


@app.post("/api/v1/security/captcha/verify", response_model=TokenResponse)
async def verify_captcha_and_issue_token(
    payload: CaptchaVerifyRequest,
    captcha: CaptchaService = Depends(captcha_service),
    tokens: TokenService = Depends(token_service),
) -> TokenResponse:
    captcha_is_valid = await captcha.verify(payload.captcha_token)

    if not captcha_is_valid:
        raise HTTPException(status_code=400, detail="Captcha inválido o expirado")

    access_token, expires_in = tokens.create_public_user_token()
    return TokenResponse(access_token=access_token, token_type="bearer", expires_in=expires_in)


@app.get("/api/v1/bike-races/active", response_model=BikeRaceResponse | NoActiveRaceResponse)
def active_bike_race(
    service: BikeRaceService = Depends(bike_race_service),
    _current_user: TokenPayload = Depends(get_current_user_from_token),
) -> BikeRaceResponse | NoActiveRaceResponse:
    race = service.get_active_race()

    if race is None:
        return NoActiveRaceResponse()

    qr_image = (
        f"data:image/jpeg;base64,{base64.b64encode(race.payment_qr_image).decode('ascii')}"
        if race.payment_qr_image
        else None
    )

    return BikeRaceResponse(
        id=race.id,
        name=race.name,
        location_name=race.location_name,
        location=race.location,
        year=race.year,
        date_of_race=race.date_of_race,
        status=race.status,
        cost=int(race.cost),
        currency=race.currency,
        qr_image=qr_image,
    )


@app.get("/api/v1/bike-teams/active", response_model=list[BikeTeamResponse])
def active_bike_teams(
    service: BikeTeamService = Depends(bike_team_service),
    _current_user: TokenPayload = Depends(get_current_user_from_token),
) -> list[BikeTeamResponse]:
    teams = service.list_active_teams()
    return [
        BikeTeamResponse(
            id=team.id,
            name=team.name.upper(),
            active=team.active,
            manager_name=team.manager_name,
            contact_phone=team.contact_phone,
            facebook_page=team.facebook_page,
            picture_url=team.picture_url,
        )
        for team in teams
    ]


@app.get("/api/v1/bikers/search", response_model=BikerSearchFoundResponse | BikerSearchNotFoundResponse)
def search_bikers(
    name: str,
    service: BikerSearchService = Depends(biker_search_service),
    _current_user: TokenPayload = Depends(get_current_user_from_token),
) -> BikerSearchFoundResponse | BikerSearchNotFoundResponse:
    """Search existing bikers for review only; this never creates a race entry."""

    try:
        results = service.search_by_name(name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not results:
        return BikerSearchNotFoundResponse()

    return BikerSearchFoundResponse(
        results=[
            BikerSearchResultResponse(
                id=result.id,
                full_name=result.full_name,
                dni=result.dni,
                birth_date=result.birth_date,
                cellphone=result.cellphone,
                team_name=result.team_name,
                category=result.category,
                last_registered_race=(
                    LastRegisteredRaceResponse(
                        id=result.last_registered_race.id,
                        name=result.last_registered_race.name,
                    )
                    if result.last_registered_race
                    else None
                ),
            )
            for result in results
        ]
    )


@app.get("/api/v1/cycling-teams/active", response_model=list[CyclingTeamResponse])
def active_cycling_teams(
    service: CyclingTeamService = Depends(cycling_team_service),
    _current_user: TokenPayload = Depends(get_current_user_from_token),
) -> list[CyclingTeamResponse]:
    return [CyclingTeamResponse(id=team.id, name=team.name) for team in service.list_active_teams()]


@app.post("/api/v1/bikers/{biker_id}/lookup-action", response_model=BikerLookupActionResponse)
def register_biker_lookup_action(
    biker_id: UUID,
    payload: BikerLookupActionRequest,
    service: BikerLookupActionService = Depends(biker_lookup_action_service),
    _current_user: TokenPayload = Depends(get_current_user_from_token),
) -> BikerLookupActionResponse:
    """Registers review/team update action without enrolling the biker again."""

    try:
        result = service.register_team_review(
            biker_id=biker_id,
            bike_race_id=payload.bike_race_id,
            searched_name=payload.searched_name,
            new_team_name=payload.new_team_name,
            confirm_action=payload.confirm_action,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return BikerLookupActionResponse(
        message=result.message,
        biker=BikerLookupActionBikerResponse(
            id=result.biker_id,
            full_name=result.full_name,
            team_name=result.team_name,
        ),
    )


def _persist_payment_proof(upload: UploadFile, file_bytes: bytes) -> Path:
    """Stores the uploaded proof in a local OCR workspace with a safe name."""

    original_name = upload.filename or ""
    extension = Path(original_name).suffix.lower()
    if extension not in SUPPORTED_PAYMENT_PROOF_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado para OCR.")

    storage_dir = settings().payment_proofs_storage_dir
    storage_dir.mkdir(parents=True, exist_ok=True)
    target_path = storage_dir / f"{uuid4().hex}{extension}"
    target_path.write_bytes(file_bytes)
    return target_path


@app.post("/api/v1/registrations/first-race/validate", response_model=RegistrationReviewResponse)
@app.post("/api/v1/registrations/first-race/review", response_model=RegistrationReviewResponse)
async def review_first_race_registration(
    dni: str = Form(...),
    dni_extension: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    birth_date: str = Form(...),
    gender: str = Form(...),
    requested_category: str = Form(...),
    bike_team_name: str = Form(...),
    payment_proof: UploadFile = File(...),
    service: RegistrationService = Depends(registration_service),
    tokens: TokenService = Depends(token_service),
    _current_user: TokenPayload = Depends(get_current_user_from_token),
) -> RegistrationReviewResponse:
    """Build the agent review card before inserting a biker registration."""

    try:
        parsed_birth_date = date.fromisoformat(birth_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="La fecha de nacimiento debe tener formato YYYY-MM-DD.") from exc

    proof_bytes = await payment_proof.read()
    proof_path = _persist_payment_proof(payment_proof, proof_bytes)

    logger.info(
        "POST /api/v1/registrations/first-race/review payload dni=%s dni_extension=%s full_name=%s email=%s birth_date=%s gender=%s requested_category=%s bike_team_name=%s proof_name=%s proof_type=%s proof_size_bytes=%s",
        dni,
        dni_extension,
        full_name,
        email,
        parsed_birth_date.isoformat(),
        gender,
        requested_category,
        bike_team_name,
        payment_proof.filename or "payment-proof",
        payment_proof.content_type or "",
        len(proof_bytes),
    )

    registration = NewBikerRegistrationInput(
        dni=dni,
        dni_extension=dni_extension,
        full_name=full_name,
        email=email,
        birth_date=parsed_birth_date,
        gender=gender,
        requested_category=requested_category,
        bike_team_name=bike_team_name,
        payment_proof_filename=payment_proof.filename or "payment-proof",
        payment_proof_content_type=payment_proof.content_type,
        payment_proof_path=proof_path,
    )

    try:
        review = service.build_first_race_review(registration)
    except GoogleVisionOcrConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail="Google OCR no está configurado correctamente. Verifique GOOGLE_APPLICATION_CREDENTIALS.",
        ) from exc
    except GoogleVisionOcrProcessingError as exc:
        raise HTTPException(status_code=503, detail="No se pudo procesar el comprobante con Google Vision OCR.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    review_token = tokens.create_registration_review_token(review.to_token_payload())
    return RegistrationReviewResponse(review_token=review_token, **review.to_token_payload())


@app.post("/api/v1/registrations/first-race/confirm", response_model=RegistrationConfirmResponse)
def confirm_first_race_registration(
    payload: RegistrationConfirmRequest,
    service: RegistrationService = Depends(registration_service),
    tokens: TokenService = Depends(token_service),
    _current_user: TokenPayload = Depends(get_current_user_from_token),
) -> RegistrationConfirmResponse:
    """Persist the biker only after Human-in-the-Loop confirmation."""

    try:
        review = RegistrationReview.from_token_payload(tokens.decode_registration_review_token(payload.review_token))
        biker = service.register_from_review(review)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=400, detail="La revisión de inscripción expiró o no es válida.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RegistrationConfirmResponse(
        id=biker.id,
        race_id=biker.race_id,
        race_name=review.race_name,
        message=f"Inscripción correcta. Bienvenido a la carrera {review.race_name}. Te esperamos en la fecha de la carrera.",
    )


@app.get("/api/v1/registrations/bulk/template")
def download_bulk_registration_template(
    _current_user: TokenPayload = Depends(get_current_user_from_token),
) -> StreamingResponse:
    """Returns the bulk template as CSV that opens cleanly in Excel."""

    template = StringIO()
    template.write("DNI,Nombre Completo,Fecha Nacimiento,Genero,Categoria\n")
    template.write("1234567,Juan Perez,1990-01-01,Masculino,Aficionado\n")
    template.seek(0)

    return StreamingResponse(
        iter([template.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="plantilla-inscripcion-masiva-cicloai.csv"'},
    )


@app.post("/api/v1/registrations/bulk/upload", response_model=BulkRegistrationResponse)
async def upload_bulk_registration_template(
    template_file: UploadFile = File(...),
    service: RegistrationService = Depends(registration_service),
    _current_user: TokenPayload = Depends(get_current_user_from_token),
) -> BulkRegistrationResponse:
    """Validates and inserts competitors from the bulk registration template."""

    file_bytes = await template_file.read()
    try:
        result = service.register_bulk_from_template(
            filename=template_file.filename or "bulk-template.csv",
            file_bytes=file_bytes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return BulkRegistrationResponse(
        race_id=result.race_id,
        race_name=result.race_name,
        inserted_competitors=result.inserted_competitors,
        unit_cost=result.unit_cost,
        currency=result.currency,
        total_amount=result.total_amount,
        message=result.message,
    )
