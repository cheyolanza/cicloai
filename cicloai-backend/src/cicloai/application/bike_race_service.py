from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from cicloai.infrastructure.models.bike_race import BikeRace, BikeRaceStatus


class BikeRaceService:
    """Reads race availability from PostgreSQL for the registration frontend."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_active_race(self) -> BikeRace | None:
        statement = (
            select(BikeRace)
            .where(BikeRace.status == BikeRaceStatus.ACTIVE.value)
            .order_by(BikeRace.created_at.desc())
            .limit(1)
        )
        return self._db.execute(statement).scalar_one_or_none()
