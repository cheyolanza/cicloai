from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from cicloai.application.payment_proof_ocr_service import PaymentOcrResult
from cicloai.application.payment_validation_service import PaymentValidationResult
from cicloai.application.registration_service import (
    BulkExcelService,
    NewBikerRegistrationInput,
    RegistrationReview,
    RegistrationService,
)


def registration_input(tmp_path: Path, **overrides) -> NewBikerRegistrationInput:
    proof = tmp_path / "proof.jpg"
    proof.write_bytes(b"image")
    values = {
        "dni": "1234567",
        "dni_extension": "SC",
        "full_name": " Juan Perez ",
        "email": " JUAN@EXAMPLE.COM ",
        "birth_date": date(1990, 1, 10),
        "gender": "Masculino",
        "requested_category": "Federado",
        "bike_team_name": " independiente ",
        "payment_proof_filename": "proof.jpg",
        "payment_proof_content_type": "image/jpeg",
        "payment_proof_path": proof,
    }
    values.update(overrides)
    return NewBikerRegistrationInput(**values)


def review_payload(**overrides) -> RegistrationReview:
    values = {
        "race_id": uuid4(),
        "race_name": "Carrera Test",
        "age": 36,
        "dni": "1234567",
        "dni_extension": "SC",
        "full_name": "Juan Perez",
        "email": "juan@example.com",
        "birth_date": date(1990, 1, 10),
        "gender": "hombre",
        "requested_category": "FEDERADO",
        "category_id": uuid4(),
        "detected_category": "Federados Master A2",
        "bike_team_name": "INDEPENDIENTE",
        "payment_id": uuid4(),
        "payment_status": "validated",
        "payment_reference": "TX-OK",
        "payment_message": "Pago validado",
        "payment_provider": "mock",
        "payment_extracted_text": "Monto Bs. 60",
        "payment_expected_amount": "60.00",
        "payment_extracted_amount": "60.00",
        "payment_currency": "BOB",
        "payment_transaction_id": "TX-OK",
        "payment_date": date(2026, 4, 26),
        "payment_bank_name": "BANCO UNION",
        "category_message": "Categoria resuelta",
        "rules_source": "categories",
    }
    values.update(overrides)
    return RegistrationReview(**values)


def service_with_mocks(db_session: Session):
    ocr_service = Mock()
    ocr_service.analyze_payment_proof.return_value = PaymentOcrResult(
        is_valid=True,
        provider="mock",
        extracted_text="Monto Bs. 60",
        confidence=1.0,
        message="OK",
    )
    validator = Mock()
    validator.validate_payment_proof.return_value = PaymentValidationResult(
        payment_id=uuid4(),
        status="validated",
        reference="TX-OK",
        message="Pago validado",
        provider="mock",
        extracted_text="Monto Bs. 60",
        extracted_amount=Decimal("60.00"),
        expected_amount=Decimal("60.00"),
        currency="BOB",
        id_transaction="TX-OK",
        payment_date=date(2026, 4, 26),
        bank_name="BANCO UNION",
    )
    return (
        RegistrationService(db_session, ocr_service, validator),
        ocr_service,
        validator,
    )


def test_bulk_excel_service_parses_csv_and_common_date_formats() -> None:
    competitors = BulkExcelService().parse(
        "bulk.csv",
        (
            "DNI,Nombre Completo,Categoria,Fecha Nacimiento,Genero\n"
            "1234567,Ana Rojas,Federado,10/01/1990,Femenino\n"
            "7654321,Luis Paz,Aficionado,45301,Masculino\n"
        ).encode("utf-8"),
    )

    assert [competitor.full_name for competitor in competitors] == [
        "Ana Rojas",
        "Luis Paz",
    ]
    assert competitors[0].birth_date == date(1990, 1, 10)
    assert competitors[1].birth_date == date(2024, 1, 10)


@pytest.mark.parametrize(
    ("filename", "content", "message"),
    [
        ("bulk.xlsx", b"", "formato CSV"),
        ("bulk.csv", b"DNI,Nombre Completo\n", "Faltan columnas"),
        (
            "bulk.csv",
            b"DNI,Nombre Completo,Categoria,Fecha Nacimiento,Genero\n",
            "no contiene competidores",
        ),
        (
            "bulk.csv",
            b"DNI,Nombre Completo,Categoria,Fecha Nacimiento,Genero\n123,Ana,Fed,1990-01-01,Femenino\n",
            "DNI inválido",
        ),
        (
            "bulk.csv",
            b"DNI,Nombre Completo,Categoria,Fecha Nacimiento,Genero\n1234567,Ana,Fed,mala,Femenino\n",
            "fecha inválida",
        ),
        (
            "bulk.csv",
            b"DNI,Nombre Completo,Categoria,Fecha Nacimiento,Genero\n1234567,Ana,Fed,1990-01-01,Otro\n",
            "género inválido",
        ),
    ],
)
def test_bulk_excel_service_rejects_invalid_templates(
    filename: str, content: bytes, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        BulkExcelService().parse(filename, content)


def test_build_first_race_review_successfully_coordinates_ocr_payment_and_category(
    db_session: Session, race_factory, category_factory, team_factory, tmp_path: Path
) -> None:
    race = race_factory(cost=Decimal("60.00"))
    category = category_factory(race_id=race.id)
    team_factory(name="INDEPENDIENTE")
    service, ocr_service, validator = service_with_mocks(db_session)

    review = service.build_first_race_review(registration_input(tmp_path))

    assert review.race_id == race.id
    assert review.full_name == "Juan Perez"
    assert review.email == "juan@example.com"
    assert review.category_id == category.id
    assert review.payment_status == "validated"
    ocr_service.analyze_payment_proof.assert_called_once()
    validator.validate_payment_proof.assert_called_once()


def test_build_first_race_review_rejects_when_no_active_race(
    db_session: Session, tmp_path: Path
) -> None:
    service, _ocr, _validator = service_with_mocks(db_session)

    with pytest.raises(ValueError, match="No hay carreras"):
        service.build_first_race_review(registration_input(tmp_path))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("dni", "123", "DNI"),
        ("dni_extension", "ZZ", "extensión"),
        ("full_name", " ", "nombre completo"),
        ("email", "invalid", "email"),
        ("gender", "otro", "sexo"),
        ("requested_category", "Pro", "tipo de categoría"),
    ],
)
def test_build_first_race_review_validates_identity_gender_and_category_type(
    db_session: Session,
    race_factory,
    team_factory,
    tmp_path: Path,
    field: str,
    value,
    message: str,
) -> None:
    race_factory()
    team_factory(name="INDEPENDIENTE")
    service, _ocr, _validator = service_with_mocks(db_session)

    with pytest.raises(ValueError, match=message):
        service.build_first_race_review(registration_input(tmp_path, **{field: value}))


def test_build_first_race_review_rejects_inactive_team(
    db_session: Session, race_factory, tmp_path: Path
) -> None:
    race_factory()
    service, _ocr, _validator = service_with_mocks(db_session)

    with pytest.raises(ValueError, match="equipo seleccionado"):
        service.build_first_race_review(registration_input(tmp_path))


def test_build_first_race_review_rejects_future_birth_date_and_rolls_back(
    db_session: Session, race_factory, team_factory, tmp_path: Path
) -> None:
    race_factory(date_of_race=date(2026, 4, 26))
    team_factory(name="INDEPENDIENTE")
    service, _ocr, _validator = service_with_mocks(db_session)

    with pytest.raises(ValueError, match="anterior"):
        service.build_first_race_review(
            registration_input(tmp_path, birth_date=date(2027, 1, 1))
        )


def test_register_bulk_from_template_inserts_pending_group(
    db_session: Session, race_factory, category_factory
) -> None:
    race = race_factory(cost=Decimal("70.00"))
    category_factory(
        race_id=race.id, age_from=30, age_to=40, born_from=1985, born_to=1995
    )
    service, _ocr, _validator = service_with_mocks(db_session)

    result = service.register_bulk_from_template(
        "bulk.csv",
        (
            "DNI,Nombre Completo,Categoria,Fecha Nacimiento,Genero\n"
            "1234567,Ana Rojas,Federado,1990-01-10,Masculino\n"
            "7654321,Luis Paz,Federado,1991-02-10,Masculino\n"
        ).encode("utf-8"),
    )

    assert result.inserted_competitors == 2
    assert result.unit_cost == 70
    assert result.total_amount == 140


def test_register_bulk_from_template_rejects_file_duplicates(
    db_session: Session, race_factory, category_factory
) -> None:
    race = race_factory()
    category_factory(race_id=race.id)
    service, _ocr, _validator = service_with_mocks(db_session)

    with pytest.raises(ValueError, match="DNI duplicado"):
        service.register_bulk_from_template(
            "bulk.csv",
            (
                "DNI,Nombre Completo,Categoria,Fecha Nacimiento,Genero\n"
                "1234567,Ana,Federado,1990-01-10,Masculino\n"
                "1234567,Luis,Federado,1991-01-10,Masculino\n"
            ).encode("utf-8"),
        )


def test_register_from_review_inserts_biker_and_attaches_payment(
    db_session: Session, race_factory, category_factory
) -> None:
    race = race_factory()
    category = category_factory(race_id=race.id)
    validator = Mock()
    service = RegistrationService(db_session, Mock(), validator)

    biker = service.register_from_review(
        review_payload(race_id=race.id, category_id=category.id)
    )

    assert biker.full_name == "Juan Perez"
    assert biker.status == "pendiente"
    validator.attach_to_biker.assert_called_once()


def test_register_from_review_rejects_unvalidated_payment(db_session: Session) -> None:
    service = RegistrationService(db_session, Mock(), Mock())

    with pytest.raises(ValueError, match="El pago no fue validado"):
        service.register_from_review(review_payload(payment_status="rejected"))


def test_register_from_review_rejects_duplicate_competitor(
    db_session: Session, race_factory, biker_factory
) -> None:
    race = race_factory()
    biker_factory(race=race, dni="1234567")
    service = RegistrationService(db_session, Mock(), Mock())

    with pytest.raises(ValueError, match="mismo DNI"):
        service.register_from_review(review_payload(race_id=race.id, dni="1234567"))


def test_registration_review_token_payload_round_trips() -> None:
    review = review_payload(category_id=None, payment_date=None, payment_bank_name=None)

    restored = RegistrationReview.from_token_payload(review.to_token_payload())

    assert restored == review
