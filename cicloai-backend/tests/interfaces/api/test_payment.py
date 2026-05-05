from __future__ import annotations

import pytest
from pydantic import ValidationError

from cicloai.interfaces.api.payment import PaymentOcrResult


def test_payment_ocr_result_schema_accepts_success_payload() -> None:
    payload = PaymentOcrResult(
        is_valid=True,
        provider="mock",
        extracted_text="Monto Bs. 60",
        confidence=1.0,
        message="OK",
    )

    assert payload.model_dump() == {
        "is_valid": True,
        "provider": "mock",
        "extracted_text": "Monto Bs. 60",
        "confidence": 1.0,
        "message": "OK",
    }


def test_payment_ocr_result_schema_requires_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PaymentOcrResult(provider="mock", message="incompleto")  # type: ignore[call-arg]

    assert {"is_valid", "extracted_text", "confidence"}.issubset(
        {error["loc"][0] for error in exc_info.value.errors()}
    )


def test_payment_ocr_result_schema_accepts_nullable_ocr_values() -> None:
    payload = PaymentOcrResult(
        is_valid=False,
        provider="mock",
        extracted_text=None,
        confidence=None,
        message="No se encontro texto",
    )

    assert payload.extracted_text is None
    assert payload.confidence is None
