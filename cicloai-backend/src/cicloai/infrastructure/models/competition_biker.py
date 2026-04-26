from __future__ import annotations

from datetime import date, datetime
from uuid import UUID as PythonUUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from cicloai.infrastructure.database.base import Base


class CompetitionBiker(Base):
    """Final registration record for a biker inside one competition.

    This table intentionally stores the category and payment result that were
    reviewed by the agent before Human-in-the-Loop confirmation. Future flows
    can share the same final table while changing only their review strategy.
    """

    __tablename__ = "competition_bikers"
    __table_args__ = (
        UniqueConstraint("race_id", "dni", "dni_extension", name="uq_competition_bikers_race_identity"),
    )

    id: Mapped[PythonUUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    race_id: Mapped[PythonUUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("bike_races.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    dni: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    dni_extension: Mapped[str] = mapped_column(String(2), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    requested_category: Mapped[str] = mapped_column(String(30), nullable=False)
    detected_category: Mapped[str] = mapped_column(String(30), nullable=False)
    bike_team_name: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(30), nullable=False)
    payment_reference: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="registered", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
