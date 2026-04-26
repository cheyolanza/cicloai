from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from cicloai.infrastructure.models.bike_race import BikeRace
from cicloai.infrastructure.models.competition_biker import CompetitionBiker


@dataclass(frozen=True)
class LastRegisteredRace:
    id: UUID
    name: str


@dataclass(frozen=True)
class BikerSearchResult:
    id: UUID
    full_name: str
    dni: str
    birth_date: date
    cellphone: str | None
    team_name: str | None
    category: str
    last_registered_race: LastRegisteredRace | None


class BikerSearchService:
    """Searches previously registered bikers without creating new registrations."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def search_by_name(self, name: str, limit: int = 10) -> list[BikerSearchResult]:
        normalized = name.strip()
        if len(normalized) < 2:
            raise ValueError("Ingresa al menos 2 caracteres para buscar.")

        statement = (
            select(CompetitionBiker, BikeRace)
            .join(BikeRace, BikeRace.id == CompetitionBiker.race_id, isouter=True)
            .where(func.upper(CompetitionBiker.full_name).like(f"%{normalized.upper()}%"))
            .order_by(func.upper(CompetitionBiker.full_name).asc())
            .limit(limit)
        )

        return [
            BikerSearchResult(
                id=biker.id,
                full_name=biker.full_name,
                dni=biker.dni,
                birth_date=biker.birth_date,
                cellphone=None,
                team_name=biker.bike_team_name,
                category=biker.detected_category,
                last_registered_race=LastRegisteredRace(id=race.id, name=race.name) if race else None,
            )
            for biker, race in self._db.execute(statement).all()
        ]
