from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from cicloai.infrastructure.models.bike_team import BikeTeam


class BikeTeamService:
    """Read service for active cycling teams.

    The query deliberately orders by uppercase display name so the frontend can
    render a stable searchable catalog without duplicating sorting rules.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_active_teams(self) -> list[BikeTeam]:
        statement = (
            select(BikeTeam)
            .where(BikeTeam.active.is_(True))
            .order_by(func.upper(BikeTeam.name).asc())
        )
        return list(self._db.execute(statement).scalars().all())
