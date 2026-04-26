from __future__ import annotations

from datetime import date
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


class BikeRaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    location_name: str
    location: str | None = None
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
