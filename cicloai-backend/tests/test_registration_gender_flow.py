from datetime import date
from unittest.mock import Mock
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cicloai.application.registration_service import (
    BulkExcelService,
    RegistrationService,
)
from cicloai.infrastructure.database.base import Base
from cicloai.infrastructure.models.bike_race import BikeRace, BikeRaceStatus
from cicloai.infrastructure.models.bike_race_category import BikeRaceCategory
from cicloai.infrastructure.models.category import Category


def test_bulk_excel_service_parses_gender_column() -> None:
    service = BulkExcelService()

    competitors = service.parse(
        filename="bulk.csv",
        file_bytes=(
            "DNI,Nombre Completo,Fecha Nacimiento,Genero,Categoria\n"
            "1234567,Juan Perez,1990-01-10,Masculino,Federado\n"
        ).encode("utf-8"),
    )

    assert len(competitors) == 1
    assert competitors[0].gender == "Masculino"
    assert competitors[0].requested_category == "Federado"


def test_registration_service_resolves_category_from_database_rules() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        race = BikeRace(
            name="Carrera Test",
            location_name="Cotoca",
            year=2026,
            date_of_race=date(2026, 4, 26),
            status=BikeRaceStatus.ACTIVE.value,
            race_cost=60,
            cost=60,
            currency="BOB",
        )
        category = Category(
            name="Federados Master A2",
            category_type="Federado",
            sex="damas",
            age_from=35,
            age_to=39,
            born_from=1990,
            born_to=1986,
            status="active",
        )
        session.add_all([race, category])
        session.flush()
        category_id = category.id
        session.add(
            BikeRaceCategory(id=uuid4(), race_id=race.id, category_id=category_id)
        )
        session.commit()

        service = RegistrationService(session, Mock(), Mock())

        result = service._resolve_category(
            birth_date=date(1990, 1, 10),
            requested_category="FEDERADO",
            gender="Femenino",
            race=race,
        )
    finally:
        session.close()
        Base.metadata.drop_all(engine)

    assert result.valid is True
    assert result.category_id == category_id
    assert result.detected_category == "Federados Master A2"
