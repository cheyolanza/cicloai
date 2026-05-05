from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from cicloai.application.admin_service import AdminService
from cicloai.infrastructure.database.base import Base
from cicloai.infrastructure.models.bike_race import BikeRace, BikeRaceStatus
from cicloai.infrastructure.models.competition_biker import CompetitionBiker
from cicloai.infrastructure.models.race_qr_payment import RaceQrPayment


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def create_race(
    db: Session, *, name: str = "Carrera Test", cost: Decimal = Decimal("60.00")
) -> BikeRace:
    race = BikeRace(
        name=name,
        location_name="Cotoca",
        year=2026,
        date_of_race=date(2026, 4, 26),
        status=BikeRaceStatus.ACTIVE.value,
        race_cost=int(cost),
        cost=cost,
        currency="BOB",
    )
    db.add(race)
    db.flush()
    return race


def create_biker(
    db: Session,
    race: BikeRace,
    *,
    full_name: str,
    status: str = "pendiente",
    payment_group_id=None,
) -> CompetitionBiker:
    dni = str(1000000 + uuid4().int % 9000000)
    biker = CompetitionBiker(
        race_id=race.id,
        payment_group_id=payment_group_id,
        full_name=full_name,
        email=f"{full_name.lower().replace(' ', '.')}@cicloai.local",
        dni=dni,
        dni_extension="SC",
        birth_date=date(1990, 1, 10),
        gender="hombre",
        requested_category="FEDERADO",
        detected_category="MASTER A",
        bike_team_name="INDEPENDIENTE",
        payment_status="validated" if status == "habilitado" else "pending",
        payment_reference="REF",
        status=status,
    )
    db.add(biker)
    db.flush()
    return biker


def create_payment(
    db: Session,
    race: BikeRace,
    proof_path: Path,
    *,
    status: str,
    expected_amount: Decimal,
    extracted_amount: Decimal | None,
    biker: CompetitionBiker | None = None,
    payment_group_id=None,
) -> RaceQrPayment:
    payment = RaceQrPayment(
        bike_race_id=race.id,
        competition_biker_id=biker.id if biker else None,
        payment_group_id=payment_group_id,
        expected_amount=expected_amount,
        extracted_amount=extracted_amount,
        currency="BOB",
        id_transaction=f"TX-{uuid4()}" if status == "validated" else None,
        payment_date=date(2026, 4, 26),
        bank_name="BANCO UNION",
        proof_file_path=str(proof_path),
        ocr_provider="test",
        ocr_text="Monto Bs. 60",
        status=status,
        rejection_reason=None if status == "validated" else "Pago pendiente",
    )
    db.add(payment)
    db.flush()
    return payment


def test_list_payments_returns_payment_with_race_and_biker_data(
    db_session: Session, tmp_path: Path
) -> None:
    race = create_race(db_session)
    biker = create_biker(db_session, race, full_name="Juan Perez", status="habilitado")
    payment = create_payment(
        db_session,
        race,
        tmp_path / "proof.jpg",
        status="validated",
        expected_amount=Decimal("60.00"),
        extracted_amount=Decimal("60.00"),
        biker=biker,
    )
    db_session.commit()

    records = AdminService(db_session).list_payments()

    assert len(records) == 1
    assert records[0].payment.id == payment.id
    assert records[0].race.name == "Carrera Test"
    assert [record_biker.full_name for record_biker in records[0].bikers] == [
        "Juan Perez"
    ]
    assert records[0].total_collected == Decimal("60.00")


def test_list_payments_total_collected_ignores_rejected_or_unenabled_payments(
    db_session: Session,
    tmp_path: Path,
) -> None:
    race = create_race(db_session)
    enabled_biker = create_biker(
        db_session, race, full_name="Ana Rojas", status="habilitado"
    )
    pending_biker = create_biker(
        db_session, race, full_name="Luis Flores", status="pendiente"
    )
    rejected_biker = create_biker(
        db_session, race, full_name="Mario Paz", status="habilitado"
    )
    create_payment(
        db_session,
        race,
        tmp_path / "validated.jpg",
        status="validated",
        expected_amount=Decimal("60.00"),
        extracted_amount=Decimal("60.00"),
        biker=enabled_biker,
    )
    create_payment(
        db_session,
        race,
        tmp_path / "pending-biker.jpg",
        status="validated",
        expected_amount=Decimal("60.00"),
        extracted_amount=Decimal("60.00"),
        biker=pending_biker,
    )
    create_payment(
        db_session,
        race,
        tmp_path / "rejected.jpg",
        status="rejected",
        expected_amount=Decimal("60.00"),
        extracted_amount=Decimal("10.00"),
        biker=rejected_biker,
    )
    db_session.commit()

    records = AdminService(db_session).list_payments()

    assert len(records) == 3
    assert {record.total_collected for record in records} == {Decimal("60.00")}


def test_list_payments_group_payment_counts_total_only_when_full_group_is_enabled(
    db_session: Session,
    tmp_path: Path,
) -> None:
    race = create_race(db_session, cost=Decimal("120.00"))
    payment_group_id = uuid4()
    create_biker(
        db_session,
        race,
        full_name="Grupo Uno",
        status="habilitado",
        payment_group_id=payment_group_id,
    )
    create_biker(
        db_session,
        race,
        full_name="Grupo Dos",
        status="pendiente",
        payment_group_id=payment_group_id,
    )
    payment = create_payment(
        db_session,
        race,
        tmp_path / "group.jpg",
        status="validated",
        expected_amount=Decimal("120.00"),
        extracted_amount=Decimal("120.00"),
        payment_group_id=payment_group_id,
    )
    db_session.commit()

    records = AdminService(db_session).list_payments()

    assert len(records) == 1
    assert records[0].payment.id == payment.id
    assert [biker.full_name for biker in records[0].bikers] == [
        "Grupo Dos",
        "Grupo Uno",
    ]
    assert records[0].total_collected == Decimal("0")
