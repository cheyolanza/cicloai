from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from cicloai.application.admin_service import (
    AdminBikerInput,
    AdminCategoryInput,
    AdminRaceInput,
    AdminService,
)
from cicloai.infrastructure.models.bike_race import BikeRaceStatus


def race_input(**overrides) -> AdminRaceInput:
    values = {
        "name": "  Nueva Carrera  ",
        "location_name": "  Cotoca  ",
        "location": "  Santa Cruz  ",
        "strava_map_html": "  <iframe></iframe>  ",
        "year": 2026,
        "date_of_race": date(2026, 4, 26),
        "status": BikeRaceStatus.DEACTIVE.value,
        "cost": Decimal("80.00"),
        "currency": "BOB",
    }
    values.update(overrides)
    return AdminRaceInput(**values)


def biker_input(**overrides) -> AdminBikerInput:
    values = {
        "full_name": "  Ana Rojas  ",
        "email": "  ANA@EXAMPLE.COM  ",
        "dni": "1234567",
        "dni_extension": "sc",
        "birth_date": date(1990, 1, 10),
        "gender": "mujer",
        "requested_category": " federado ",
        "detected_category": "Master A2",
        "bike_team_name": " independiente ",
        "payment_status": "validated",
        "payment_reference": "TX-1",
        "status": "habilitado",
    }
    values.update(overrides)
    return AdminBikerInput(**values)


def category_input(**overrides) -> AdminCategoryInput:
    values = {
        "name": " Master A2 ",
        "category_type": "Federado",
        "sex": "varones",
        "age_from": 35,
        "age_to": 39,
        "born_from": 1986,
        "born_to": 1990,
        "race_ids": [],
    }
    values.update(overrides)
    return AdminCategoryInput(**values)


def test_dashboard_metrics_reports_no_active_race(db_session: Session) -> None:
    metrics = AdminService(db_session).dashboard_metrics()

    assert metrics.active_race_id is None
    assert metrics.active_race_registered_bikers == 0


def test_dashboard_metrics_counts_registered_bikers(
    db_session: Session, race_factory, biker_factory
) -> None:
    race = race_factory()
    biker_factory(race=race)
    biker_factory(race=race, full_name="Luis Flores")

    metrics = AdminService(db_session).dashboard_metrics()

    assert metrics.active_race_id == race.id
    assert metrics.active_race_name == "Carrera Test"
    assert metrics.active_race_registered_bikers == 2


def test_create_race_trims_fields_and_rejects_second_active_race(
    db_session: Session, race_factory
) -> None:
    service = AdminService(db_session)

    race = service.create_race(race_input())

    assert race.name == "Nueva Carrera"
    assert race.location_name == "Cotoca"
    assert race.race_cost == 80

    race_factory(name="Activa")
    with pytest.raises(ValueError, match="Solo puede existir"):
        service.create_race(race_input(status=BikeRaceStatus.ACTIVE.value))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("name", " ", "nombre"),
        ("location_name", " ", "ubicación"),
        ("year", 1999, "gestión"),
        ("status", "paused", "estado"),
        ("currency", "EUR", "moneda"),
        ("cost", Decimal("-1"), "negativo"),
    ],
)
def test_create_race_validates_required_fields(
    db_session: Session, field: str, value, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        AdminService(db_session).create_race(race_input(**{field: value}))


def test_update_biker_normalizes_fields_and_status(
    db_session: Session, race_factory, biker_factory
) -> None:
    biker = biker_factory(race=race_factory())

    updated = AdminService(db_session).update_biker(biker.id, biker_input())

    assert updated.full_name == "Ana Rojas"
    assert updated.email == "ana@example.com"
    assert updated.dni_extension == "SC"
    assert updated.requested_category == "FEDERADO"
    assert updated.bike_team_name == "INDEPENDIENTE"
    assert updated.status == "habilitado"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("full_name", " ", "nombre"),
        ("email", " ", "email"),
        ("dni", "123", "DNI"),
        ("dni_extension", " ", "extensión"),
        ("gender", "otro", "sexo"),
        ("requested_category", " ", "solicitada"),
        ("detected_category", " ", "detectada"),
        ("bike_team_name", " ", "equipo"),
        ("payment_status", " ", "estado de pago"),
        ("payment_reference", " ", "referencia"),
        ("status", "otro", "estado del corredor"),
    ],
)
def test_update_biker_validates_required_fields(
    db_session: Session,
    race_factory,
    biker_factory,
    field: str,
    value,
    message: str,
) -> None:
    biker = biker_factory(race=race_factory())

    with pytest.raises(ValueError, match=message):
        AdminService(db_session).update_biker(biker.id, biker_input(**{field: value}))


def test_create_update_and_list_category_with_race_links(
    db_session: Session, race_factory
) -> None:
    race = race_factory()
    service = AdminService(db_session)

    category = service.create_category(category_input(race_ids=[race.id, race.id]))
    record = service.category_record(category.id)

    assert record.category.name == "Master A2"
    assert [linked.id for linked in record.races] == [race.id]

    updated = service.update_category(
        category.id, category_input(name="Master B1", age_from=40, age_to=44)
    )
    assert updated.name == "Master B1"
    assert service.category_record(category.id).races == []


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"name": " "}, "nombre"),
        ({"sex": "mixto"}, "sexo"),
        ({"category_type": "Pro"}, "tipo"),
        ({"age_from": -1}, "negativa"),
        ({"age_from": 40, "age_to": 30}, "mayor o igual"),
        ({"born_from": 1899}, "nacimiento desde"),
        ({"born_to": 3000}, "nacimiento hasta"),
    ],
)
def test_create_category_validates_business_fields(
    db_session: Session, payload: dict, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        AdminService(db_session).create_category(category_input(**payload))


def test_update_category_status_rejects_invalid_status(
    db_session: Session, category_factory
) -> None:
    category = category_factory()

    with pytest.raises(ValueError, match="estado"):
        AdminService(db_session).update_category_status(category.id, "archived")


def test_list_bikers_filters_sorts_and_clamps_pagination(
    db_session: Session, race_factory, biker_factory
) -> None:
    race = race_factory()
    biker_factory(race=race, full_name="Zeta Rider", status="pendiente")
    biker_factory(race=race, full_name="Ana Rider", status="habilitado")

    result = AdminService(db_session).list_bikers(
        race.id,
        page=-3,
        page_size=500,
        search="Rider",
        sort_by="full_name",
        sort_direction="asc",
    )

    assert result.total == 2
    assert [biker.full_name for biker, _payment in result.items] == [
        "Ana Rider",
        "Zeta Rider",
    ]


def test_validate_individual_payment_enables_biker(
    db_session: Session, race_factory, biker_factory, payment_factory
) -> None:
    race = race_factory()
    biker = biker_factory(race=race)
    payment = payment_factory(
        race=race, biker=biker, status="pending", transaction_id="TX-OK"
    )

    record = AdminService(db_session).validate_payment(payment.id)

    assert record.payment.status == "validated"
    assert record.bikers[0].status == "habilitado"
    assert record.bikers[0].payment_reference == "TX-OK"
    assert record.total_collected == Decimal("60.00")


def test_validate_payment_rejects_unassociated_payment(
    db_session: Session, race_factory, payment_factory
) -> None:
    payment = payment_factory(race=race_factory(), status="pending")

    with pytest.raises(ValueError, match="no tiene corredores"):
        AdminService(db_session).validate_payment(payment.id)


def test_validate_group_payment_requires_complete_group(
    db_session: Session, race_factory, biker_factory, payment_factory
) -> None:
    race = race_factory(cost=Decimal("120.00"))
    group_id = uuid4()
    biker_factory(race=race, full_name="Uno", payment_group_id=group_id)
    biker_factory(race=race, full_name="Dos", payment_group_id=group_id)
    payment = payment_factory(
        race=race,
        payment_group_id=group_id,
        status="pending",
        expected_amount=Decimal("120.00"),
    )

    record = AdminService(db_session).validate_payment(payment.id)

    assert {biker.status for biker in record.bikers} == {"habilitado"}
    assert record.total_collected == Decimal("120.00")


def test_get_payment_proof_path_requires_existing_file(
    db_session: Session, race_factory, payment_factory, tmp_path: Path
) -> None:
    existing = tmp_path / "proof.jpg"
    existing.write_bytes(b"ok")
    payment = payment_factory(race=race_factory(), proof_path=existing)

    assert AdminService(db_session).get_payment_proof_path(payment.id) == existing

    missing = payment_factory(
        race=race_factory(name="Otra"), proof_path=tmp_path / "missing.jpg"
    )
    with pytest.raises(ValueError, match="no existe"):
        AdminService(db_session).get_payment_proof_path(missing.id)


def test_missing_entities_raise_business_errors(db_session: Session) -> None:
    service = AdminService(db_session)
    missing = uuid4()

    with pytest.raises(ValueError, match="carrera"):
        service.list_bikers_for_export(missing)
    with pytest.raises(ValueError, match="corredor"):
        service.update_biker_status(missing, "habilitado")
    with pytest.raises(ValueError, match="categoría"):
        service.category_record(missing)
    with pytest.raises(ValueError, match="pago"):
        service.validate_payment(missing)
