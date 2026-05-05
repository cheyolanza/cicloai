from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from cicloai.application.payment_proof_ocr_service import PaymentOcrResult
from cicloai.application.payment_validation_service import PaymentValidationService
from cicloai.infrastructure.models.race_qr_payment import RaceQrPayment


def ocr(
    text: str | None, *, valid: bool = True, message: str = "OK"
) -> PaymentOcrResult:
    return PaymentOcrResult(
        is_valid=valid,
        provider="mock",
        extracted_text=text,
        confidence=1.0 if valid else None,
        message=message,
    )


def write_proof(tmp_path: Path) -> Path:
    path = tmp_path / "proof.jpg"
    path.write_bytes(b"fake-image")
    return path


def test_validate_payment_proof_approves_matching_ocr_data(
    db_session: Session, race_factory, tmp_path: Path
) -> None:
    race = race_factory(cost=Decimal("60.00"))
    service = PaymentValidationService(db_session)

    result = service.validate_payment_proof(
        race=race,
        ocr_result=ocr(
            "Banco Union\nMonto: Bs. 60.00\nFecha: 2026-04-26\nID Transaccion: ABC123456"
        ),
        proof_path=write_proof(tmp_path),
        expected_amount=Decimal("60.00"),
        current_date=date(2026, 4, 26),
    )

    assert result.status == "validated"
    assert result.is_valid is True
    assert result.reference == "ABC123456"
    assert result.bank_name == "BANCO UNION"
    payment = db_session.get(RaceQrPayment, result.payment_id)
    assert payment is not None
    assert payment.id_transaction == "ABC123456"
    assert payment.status == "validated"


@pytest.mark.parametrize(
    ("text", "message_fragment"),
    [
        (
            "Banco Union\nMonto Bs. 59\nFecha 26/04/2026\nNro. 1234567890",
            "no coincide",
        ),
        (
            "Banco Union\nMonto Bs. 60\nFecha 26/04/2026",
            "id de transacción",
        ),
        (
            "Monto Bs. 60\nFecha 26/04/2026\nNro. 1234567890",
            "banco",
        ),
        (
            "Banco Union\nMonto Bs. 60\nNro. 1234567890",
            "fecha válida",
        ),
        (
            "Banco Union\nMonto Bs. 60\nFecha 25/04/2026\nNro. 1234567890",
            "día de hoy",
        ),
    ],
)
def test_validate_payment_proof_rejects_invalid_ocr_business_data(
    db_session: Session,
    race_factory,
    tmp_path: Path,
    text: str,
    message_fragment: str,
) -> None:
    race = race_factory()

    result = PaymentValidationService(db_session).validate_payment_proof(
        race=race,
        ocr_result=ocr(text),
        proof_path=write_proof(tmp_path),
        expected_amount=Decimal("60.00"),
        current_date=date(2026, 4, 26),
    )

    assert result.status == "rejected"
    assert message_fragment in result.message
    payment = db_session.get(RaceQrPayment, result.payment_id)
    assert payment is not None
    assert payment.status == "rejected"
    assert payment.id_transaction is None


def test_validate_payment_proof_rejects_ocr_adapter_failure(
    db_session: Session, race_factory, tmp_path: Path
) -> None:
    result = PaymentValidationService(db_session).validate_payment_proof(
        race=race_factory(),
        ocr_result=ocr(None, valid=False, message="Imagen ilegible"),
        proof_path=write_proof(tmp_path),
        expected_amount=Decimal("60.00"),
        current_date=date(2026, 4, 26),
    )

    assert result.status == "rejected"
    assert result.message == "Imagen ilegible"


def test_validate_payment_proof_rejects_duplicate_transaction_id(
    db_session: Session, race_factory, payment_factory, tmp_path: Path
) -> None:
    race = race_factory()
    payment_factory(race=race, status="validated", transaction_id="DUP123456")

    result = PaymentValidationService(db_session).validate_payment_proof(
        race=race,
        ocr_result=ocr(
            "Banco Union\nMonto Bs. 60\nFecha 26-04-2026\nID Transaccion: DUP123456"
        ),
        proof_path=write_proof(tmp_path),
        expected_amount=Decimal("60.00"),
        current_date=date(2026, 4, 26),
    )

    assert result.status == "rejected"
    assert "ya fue registrado" in result.message


def test_attach_to_biker_requires_existing_validated_payment(
    db_session: Session, race_factory, biker_factory, payment_factory
) -> None:
    race = race_factory()
    biker = biker_factory(race=race)
    payment = payment_factory(race=race, status="validated")

    PaymentValidationService(db_session).attach_to_biker(payment.id, biker.id)

    assert payment.competition_biker_id == biker.id


def test_attach_to_biker_rejects_missing_or_unvalidated_payment(
    db_session: Session, race_factory, payment_factory
) -> None:
    race = race_factory()
    rejected = payment_factory(race=race, status="rejected")
    service = PaymentValidationService(db_session)

    with pytest.raises(ValueError, match="No se encontró"):
        service.attach_to_biker(race.id, race.id)
    with pytest.raises(ValueError, match="no está validado"):
        service.attach_to_biker(rejected.id, race.id)


def test_extract_payment_data_supports_bank_regex_and_textual_dates() -> None:
    result = PaymentValidationService(db=None).extract_payment_data(  # type: ignore[arg-type]
        "Banco: Solidez Digital\nTotal BOB 75,50\n21 de Abril, 2026\nReferencia: XYZ-98765"
    )

    assert result.amount == Decimal("75.50")
    assert result.payment_date == date(2026, 4, 21)
    assert result.bank_name == "BANCO SOLIDEZ DIGITAL"
    assert result.id_transaction == "XYZ-98765"
