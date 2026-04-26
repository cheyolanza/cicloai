from __future__ import annotations

from pydantic import BaseModel


class PaymentOcrResult(BaseModel):
    """HTTP-safe OCR result contract shared by payment flows.

    The domain service currently returns an equivalent dataclass to keep the
    use case independent from FastAPI/Pydantic. This schema documents the API
    shape expected by frontend and future payment endpoints.
    """

    is_valid: bool
    provider: str
    extracted_text: str | None
    confidence: float | None
    message: str
