from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from cicloai.infrastructure.database.session import SessionLocal
from cicloai.infrastructure.models.bike_race import BikeRace, BikeRaceStatus
from cicloai.infrastructure.models.bike_team import BikeTeam
from cicloai.infrastructure.models.cycling_team import CyclingTeam

SEED_RACE_NAME = "Primera Fecha Municipal 2026"
SEED_RACE_YEAR = 2026
SEED_RACE_COST = 60
SEED_RACE_COST_DECIMAL = Decimal("60.00")
SEED_RACE_CURRENCY = "BOB"
SEED_PAYMENT_QR_IMAGE = Path(__file__).resolve().parents[4] / "assets" / "payment_qr_2_2026_apertura.jpeg"
SEED_TEAM_NAMES = (
    "INDEPENDIENTE",
    "Team Gladiadores",
    "Team Domadores",
    "Evolution",
    "Bikers SCZ",
    "Bikerz",
    "Team Keance",
)
SEED_CYCLING_TEAM_NAMES = (
    "Independiente",
    "Team Santa Cruz",
    "Cotoca Bike Team",
    "MTB Bolivia",
)


def seed_bike_races() -> None:
    """Seed or update the active race once; reruns keep payment data current."""
    db = SessionLocal()
    try:
        existing = db.execute(
            select(BikeRace).where(BikeRace.name == SEED_RACE_NAME, BikeRace.year == SEED_RACE_YEAR)
        ).scalar_one_or_none()
        qr_image = SEED_PAYMENT_QR_IMAGE.read_bytes() if SEED_PAYMENT_QR_IMAGE.exists() else None

        if existing is not None:
            existing.race_cost = SEED_RACE_COST
            existing.cost = SEED_RACE_COST_DECIMAL
            existing.currency = SEED_RACE_CURRENCY
            existing.payment_qr_image = qr_image
            db.commit()
            return

        db.add(
            BikeRace(
                name=SEED_RACE_NAME,
                location_name="Parada Trenes Cotoca",
                location=None,
                year=SEED_RACE_YEAR,
                date_of_race=None,
                status=BikeRaceStatus.ACTIVE.value,
                race_cost=SEED_RACE_COST,
                cost=SEED_RACE_COST_DECIMAL,
                currency=SEED_RACE_CURRENCY,
                payment_qr_image=qr_image,
            )
        )
        db.commit()
    finally:
        db.close()


def seed_bike_teams() -> None:
    """Seed the team catalog idempotently for the registration combo box."""
    db = SessionLocal()
    try:
        for team_name in SEED_TEAM_NAMES:
            existing = db.execute(select(BikeTeam).where(BikeTeam.name == team_name)).scalar_one_or_none()

            if existing is None:
                db.add(BikeTeam(name=team_name, active=True))

        db.commit()
    finally:
        db.close()


def seed_cycling_teams() -> None:
    """Seed the existing-biker team catalog idempotently."""
    db = SessionLocal()
    try:
        for team_name in SEED_CYCLING_TEAM_NAMES:
            existing = db.execute(select(CyclingTeam).where(CyclingTeam.name == team_name)).scalar_one_or_none()
            if existing is None:
                db.add(CyclingTeam(name=team_name, status="active"))
            else:
                existing.status = "active"

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_bike_races()
    seed_bike_teams()
    seed_cycling_teams()
