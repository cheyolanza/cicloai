from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID as PythonUUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from cicloai.infrastructure.database.base import Base


class RaceQrPayment(Base):
    """OCR-derived payment proof attached to a race registration attempt.

    The record is created during the review phase, before the Human-in-the-Loop
    confirmation inserts the biker. That lets CicloAI reject bad proofs while
    keeping the registration data alive in the signed review token. Once the
    user confirms, the payment row is linked to `competition_bikers`.
    """

    __tablename__ = "race_qr_payments"
    __table_args__ = (
        UniqueConstraint("id_transaction", name="uq_race_qr_payments_id_transaction"),
    )

    id: Mapped[PythonUUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    bike_race_id: Mapped[PythonUUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("bike_races.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    competition_biker_id: Mapped[PythonUUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("competition_bikers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    expected_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    extracted_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BOB")
    id_transaction: Mapped[str | None] = mapped_column(String(120), nullable=True)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    proof_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    ocr_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
