from __future__ import annotations

from datetime import datetime
from uuid import UUID as PythonUUID, uuid4

from sqlalchemy import DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from cicloai.infrastructure.database.base import Base


class Category(Base):
    """Admin-managed race category catalog."""

    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint(
            "name", "sex", "category_type", name="uq_categories_name_sex_type"
        ),
    )

    id: Mapped[PythonUUID] = mapped_column(
        PostgresUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Federado", index=True
    )
    sex: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    age_from: Mapped[int] = mapped_column(Integer, nullable=False)
    age_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    born_from: Mapped[int] = mapped_column(Integer, nullable=False)
    born_to: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
