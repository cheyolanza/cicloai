from __future__ import annotations

from datetime import datetime
from uuid import UUID as PythonUUID, uuid4

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from cicloai.infrastructure.database.base import Base


class BikeRaceCategory(Base):
    """Category enabled for a specific race."""

    __tablename__ = "bike_race_categories"
    __table_args__ = (
        UniqueConstraint("race_id", "category_id", name="uq_bike_race_categories_pair"),
    )

    id: Mapped[PythonUUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    race_id: Mapped[PythonUUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("bike_races.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[PythonUUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
