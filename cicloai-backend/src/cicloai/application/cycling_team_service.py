from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from cicloai.infrastructure.models.cycling_team import CyclingTeam


class CyclingTeamService:
    """Reads and validates the active team catalog for lookup flows."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_active_teams(self) -> list[CyclingTeam]:
        statement = (
            select(CyclingTeam)
            .where(CyclingTeam.status == "active")
            .order_by(func.upper(CyclingTeam.name).asc())
        )
        return list(self._db.execute(statement).scalars())

    def get_active_by_name(self, team_name: str) -> CyclingTeam | None:
        statement = select(CyclingTeam).where(
            CyclingTeam.status == "active",
            func.upper(CyclingTeam.name) == team_name.strip().upper(),
        )
        return self._db.execute(statement).scalar_one_or_none()
