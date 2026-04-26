from __future__ import annotations

from datetime import datetime
from uuid import UUID as PythonUUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from cicloai.infrastructure.database.base import Base


class BikerLookupAction(Base):
    """Audit record for existing-biker lookup and team review actions."""

    __tablename__ = "biker_lookup_actions"

    id: Mapped[PythonUUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    competition_biker_id: Mapped[PythonUUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("competition_bikers.id", ondelete="RESTRICT"), nullable=False
    )
    bike_race_id: Mapped[PythonUUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("bike_races.id", ondelete="SET NULL"), nullable=True
    )
    searched_name: Mapped[str] = mapped_column(String(150), nullable=False)
    previous_team_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    new_team_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
