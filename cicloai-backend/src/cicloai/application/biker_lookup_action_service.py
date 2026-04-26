from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from cicloai.application.cycling_team_service import CyclingTeamService
from cicloai.infrastructure.models.biker_lookup_action import BikerLookupAction
from cicloai.infrastructure.models.competition_biker import CompetitionBiker


@dataclass(frozen=True)
class BikerLookupActionResult:
    biker_id: UUID
    full_name: str
    team_name: str
    message: str


class BikerLookupActionService:
    """Registers existing-biker review actions without enrolling them again."""

    def __init__(self, db: Session, cycling_teams: CyclingTeamService) -> None:
        self._db = db
        self._cycling_teams = cycling_teams

    def register_team_review(
        self,
        biker_id: UUID,
        bike_race_id: UUID | None,
        searched_name: str,
        new_team_name: str,
        confirm_action: bool,
    ) -> BikerLookupActionResult:
        if not confirm_action:
            raise ValueError("La acción debe ser confirmada para registrarse.")

        biker = self._db.get(CompetitionBiker, biker_id)
        if biker is None:
            raise ValueError("El ciclista seleccionado no existe.")

        team = self._cycling_teams.get_active_by_name(new_team_name)
        if team is None:
            raise ValueError("El equipo seleccionado no existe o no está activo.")

        previous_team_name = biker.bike_team_name
        normalized_new_team = team.name
        action_type = "team_updated" if (previous_team_name or "").upper() != normalized_new_team.upper() else "lookup_found"

        biker.bike_team_name = normalized_new_team
        self._db.add(
            BikerLookupAction(
                competition_biker_id=biker.id,
                bike_race_id=bike_race_id,
                searched_name=searched_name.strip(),
                previous_team_name=previous_team_name,
                new_team_name=normalized_new_team,
                action_type=action_type,
                status="completed",
            )
        )
        self._db.commit()
        self._db.refresh(biker)

        return BikerLookupActionResult(
            biker_id=biker.id,
            full_name=biker.full_name,
            team_name=biker.bike_team_name,
            message="Datos actualizados correctamente. El equipo fue registrado para el ciclista seleccionado.",
        )
