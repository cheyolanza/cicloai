from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IngestRequest(BaseModel):
    text: str = Field(..., min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)
    document_id: str | None = None


class IngestResponse(BaseModel):
    document_id: str
    chunks_indexed: int
    metadata: dict[str, str]


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=10)


class SourceResponse(BaseModel):
    document_id: str
    chunk_id: str
    score: float
    text: str
    metadata: dict[str, str]


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
    model: str
    latency_ms: float


class RecaptchaVerifyRequest(BaseModel):
    token: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)


class RecaptchaVerifyResponse(BaseModel):
    valid: bool
    score: float | None = None
    action: str
    reasons: list[str] = Field(default_factory=list)


class CaptchaVerifyRequest(BaseModel):
    captcha_token: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    username: str


class AdminSessionResponse(BaseModel):
    username: str


class AdminDashboardResponse(BaseModel):
    active_race_id: UUID | None = None
    active_race_name: str | None = None
    active_race_registered_bikers: int


class AdminRaceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    location_name: str = Field(..., min_length=1, max_length=150)
    location: str | None = None
    strava_map_html: str | None = None
    year: int = Field(..., ge=2000)
    date_of_race: date | None = None
    status: Literal["active", "deactive"]
    cost: Decimal = Field(..., ge=0)
    currency: Literal["BOB", "USD"]


class AdminRaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    location_name: str
    location: str | None = None
    strava_map_html: str | None = None
    year: int
    date_of_race: date | None = None
    status: Literal["active", "deactive"]
    cost: Decimal
    currency: Literal["BOB", "USD"]
    registered_bikers: int = 0
    created_at: datetime
    updated_at: datetime


class AdminCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category_type: Literal["Cicloturista", "Aficionado", "Federado"]
    sex: Literal["varones", "damas"]
    age_from: int = Field(..., ge=0)
    age_to: int | None = Field(default=None, ge=0)
    born_from: int = Field(..., ge=1900)
    born_to: int = Field(..., ge=1900)
    race_ids: list[UUID] = Field(default_factory=list)


class AdminCategoryStatusRequest(BaseModel):
    status: Literal["active", "deactive"]


class AdminCategoryResponse(BaseModel):
    id: UUID
    name: str
    category_type: Literal["Cicloturista", "Aficionado", "Federado"]
    sex: Literal["varones", "damas"]
    age_from: int
    age_to: int | None = None
    born_from: int
    born_to: int
    race_ids: list[UUID] = Field(default_factory=list)
    race_names: list[str] = Field(default_factory=list)
    status: Literal["active", "deactive"]
    created_at: datetime
    updated_at: datetime


class AdminBikerStatusRequest(BaseModel):
    status: Literal["habilitado", "deshabilitado", "pendiente"]


class AdminBikerRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=150)
    email: str = Field(..., min_length=1, max_length=254)
    dni: str = Field(..., min_length=7, max_length=7)
    dni_extension: str = Field(..., min_length=1, max_length=2)
    birth_date: date
    gender: Literal["hombre", "mujer"]
    requested_category: str = Field(..., min_length=1, max_length=30)
    detected_category: str = Field(..., min_length=1, max_length=30)
    bike_team_name: str = Field(..., min_length=1, max_length=100)
    payment_status: str = Field(..., min_length=1, max_length=30)
    payment_reference: str = Field(..., min_length=1, max_length=80)
    status: Literal["habilitado", "deshabilitado", "pendiente"]


class AdminBikerResponse(BaseModel):
    id: UUID
    race_id: UUID
    full_name: str
    email: str
    dni: str
    dni_extension: str
    birth_date: date
    gender: Literal["hombre", "mujer"]
    age: int
    requested_category: str
    detected_category: str
    bike_team_name: str
    payment_status: str
    payment_reference: str
    status: Literal["habilitado", "deshabilitado", "pendiente"]
    created_at: datetime
    updated_at: datetime
    payment_id: UUID | None = None
    payment_proof_url: str | None = None


class AdminBikerListResponse(BaseModel):
    items: list[AdminBikerResponse]
    total: int
    page: int
    page_size: int


class AdminPaymentBikerResponse(BaseModel):
    id: UUID
    full_name: str
    status: Literal["habilitado", "deshabilitado", "pendiente"]


class AdminPaymentResponse(BaseModel):
    id: UUID
    race_id: UUID
    race_name: str
    race_location_name: str
    race_year: int
    created_at: datetime
    transaction_id: str | None = None
    extracted_amount: Decimal | None = None
    validated_amount: Decimal | None = None
    expected_amount: Decimal
    currency: Literal["BOB", "USD"]
    total_collected: Decimal
    payment_proof_url: str
    status: str
    payment_kind: Literal["individual", "grupal"]
    biker_count: int
    enabled_biker_count: int
    can_validate: bool
    bikers: list[AdminPaymentBikerResponse]


class BikeRaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    location_name: str
    location: str | None = None
    strava_map_html: str | None = None
    year: int
    date_of_race: date | None = None
    status: Literal["active", "deactive"]
    cost: int
    currency: Literal["BOB", "USD"]
    qr_image: str | None = None


class NoActiveRaceResponse(BaseModel):
    message: str = "No hay carreras habilitadas actualmente"


class BikeTeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    active: bool
    manager_name: str | None = None
    contact_phone: str | None = None
    facebook_page: str | None = None
    picture_url: str | None = None


class RegistrationReviewResponse(BaseModel):
    review_token: str
    race_id: UUID
    race_name: str
    age: int
    dni: str
    dni_extension: str
    full_name: str
    email: str
    birth_date: date
    requested_category: str
    detected_category: str
    bike_team_name: str
    payment_id: UUID
    payment_status: str
    payment_reference: str
    payment_message: str
    payment_provider: str
    payment_extracted_text: str | None = None
    payment_expected_amount: str
    payment_extracted_amount: str | None = None
    payment_currency: str
    payment_transaction_id: str | None = None
    payment_date: str | None = None
    payment_bank_name: str | None = None
    category_message: str
    rules_source: str


class RegistrationConfirmRequest(BaseModel):
    review_token: str = Field(..., min_length=1)


class RegistrationConfirmResponse(BaseModel):
    id: UUID
    race_id: UUID
    race_name: str
    message: str


class BulkRegistrationResponse(BaseModel):
    race_id: UUID
    race_name: str
    inserted_competitors: int
    unit_cost: int
    currency: Literal["BOB", "USD"]
    total_amount: int
    message: str


class LastRegisteredRaceResponse(BaseModel):
    id: UUID
    name: str


class BikerSearchResultResponse(BaseModel):
    id: UUID
    full_name: str
    dni: str
    birth_date: date
    cellphone: str | None = None
    team_name: str | None = None
    category: str
    last_registered_race: LastRegisteredRaceResponse | None = None


class BikerSearchFoundResponse(BaseModel):
    status: Literal["found"] = "found"
    results: list[BikerSearchResultResponse]


class BikerSearchNotFoundResponse(BaseModel):
    status: Literal["not_found"] = "not_found"
    message: str = "No se encontraron ciclistas con ese nombre."


class CyclingTeamResponse(BaseModel):
    id: UUID
    name: str


class BikerLookupActionRequest(BaseModel):
    bike_race_id: UUID | None = None
    searched_name: str = Field(..., min_length=1, max_length=150)
    new_team_name: str = Field(..., min_length=1, max_length=150)
    confirm_action: bool


class BikerLookupActionBikerResponse(BaseModel):
    id: UUID
    full_name: str
    team_name: str


class BikerLookupActionResponse(BaseModel):
    status: Literal["completed"] = "completed"
    message: str
    biker: BikerLookupActionBikerResponse
    next_action: Literal["CONTINUE_TO_PAYMENT_LATER"] = "CONTINUE_TO_PAYMENT_LATER"


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class AgentChatSourceResponse(BaseModel):
    source_file: str
    chunk_id: str | None = None


class AgentChatUiActionResponse(BaseModel):
    type: Literal["SHOW_SINGLE_REGISTRATION", "SHOW_BULK_REGISTRATION", "NONE"]


class AgentChatResponse(BaseModel):
    answer: str
    sources: list[AgentChatSourceResponse] = Field(default_factory=list)
    intent: Literal["rag_answer", "start_single_registration", "start_bulk_registration"]
    ui_action: AgentChatUiActionResponse | None = None
