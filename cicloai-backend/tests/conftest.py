from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from cicloai.infrastructure.database.base import Base
from cicloai.infrastructure.models.bike_race import BikeRace, BikeRaceStatus
from cicloai.infrastructure.models.bike_race_category import BikeRaceCategory
from cicloai.infrastructure.models.bike_team import BikeTeam
from cicloai.infrastructure.models.category import Category
from cicloai.infrastructure.models.competition_biker import CompetitionBiker
from cicloai.infrastructure.models.race_qr_payment import RaceQrPayment


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def race_factory(db_session: Session):
    def create_race(
        *,
        name: str = "Carrera Test",
        status: str = BikeRaceStatus.ACTIVE.value,
        cost: Decimal = Decimal("60.00"),
        date_of_race: date | None = date(2026, 4, 26),
    ) -> BikeRace:
        race = BikeRace(
            name=name,
            location_name="Cotoca",
            location="Santa Cruz",
            strava_map_html=None,
            year=2026,
            date_of_race=date_of_race,
            status=status,
            race_cost=int(cost),
            cost=cost,
            currency="BOB",
        )
        db_session.add(race)
        db_session.flush()
        return race

    return create_race


@pytest.fixture()
def category_factory(db_session: Session):
    def create_category(
        *,
        race_id: UUID | None = None,
        name: str = "Federados Master A2",
        category_type: str = "Federado",
        sex: str = "varones",
        age_from: int = 35,
        age_to: int | None = 39,
        born_from: int = 1986,
        born_to: int = 1990,
        status: str = "active",
    ) -> Category:
        category = Category(
            name=name,
            category_type=category_type,
            sex=sex,
            age_from=age_from,
            age_to=age_to,
            born_from=born_from,
            born_to=born_to,
            status=status,
        )
        db_session.add(category)
        db_session.flush()
        if race_id is not None:
            db_session.add(BikeRaceCategory(race_id=race_id, category_id=category.id))
            db_session.flush()
        return category

    return create_category


@pytest.fixture()
def team_factory(db_session: Session):
    def create_team(*, name: str = "INDEPENDIENTE", active: bool = True) -> BikeTeam:
        team = BikeTeam(name=name, active=active)
        db_session.add(team)
        db_session.flush()
        return team

    return create_team


@pytest.fixture()
def biker_factory(db_session: Session):
    def create_biker(
        *,
        race: BikeRace,
        full_name: str = "Juan Perez",
        dni: str | None = None,
        status: str = "pendiente",
        payment_group_id: UUID | None = None,
    ) -> CompetitionBiker:
        identifier = dni or str(1000000 + uuid4().int % 9000000)
        biker = CompetitionBiker(
            race_id=race.id,
            payment_group_id=payment_group_id,
            full_name=full_name,
            email=f"{identifier}@cicloai.local",
            dni=identifier,
            dni_extension="SC",
            birth_date=date(1990, 1, 10),
            gender="hombre",
            requested_category="FEDERADO",
            detected_category="Federados Master A2",
            bike_team_name="INDEPENDIENTE",
            payment_status="pending",
            payment_reference="REF",
            status=status,
        )
        db_session.add(biker)
        db_session.flush()
        return biker

    return create_biker


@pytest.fixture()
def payment_factory(db_session: Session, tmp_path: Path):
    def create_payment(
        *,
        race: BikeRace,
        status: str = "pending",
        expected_amount: Decimal = Decimal("60.00"),
        extracted_amount: Decimal | None = Decimal("60.00"),
        biker: CompetitionBiker | None = None,
        payment_group_id: UUID | None = None,
        proof_path: Path | None = None,
        transaction_id: str | None = None,
    ) -> RaceQrPayment:
        path = proof_path or tmp_path / f"{uuid4()}.jpg"
        payment = RaceQrPayment(
            bike_race_id=race.id,
            competition_biker_id=biker.id if biker else None,
            payment_group_id=payment_group_id,
            expected_amount=expected_amount,
            extracted_amount=extracted_amount,
            currency="BOB",
            id_transaction=transaction_id,
            payment_date=date(2026, 4, 26),
            bank_name="BANCO UNION",
            proof_file_path=str(path),
            ocr_provider="test",
            ocr_text="Monto Bs. 60",
            status=status,
            rejection_reason=None if status == "validated" else "Pendiente",
        )
        db_session.add(payment)
        db_session.flush()
        return payment

    return create_payment
