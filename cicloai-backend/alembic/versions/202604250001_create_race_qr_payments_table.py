"""create race qr payments table

Revision ID: 202604250001
Revises: 202604240009
Create Date: 2026-04-25 00:01:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202604250001"
down_revision: str | None = "202604240009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "race_qr_payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("bike_race_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("competition_biker_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("expected_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("extracted_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="BOB"),
        sa.Column("id_transaction", sa.String(length=120), nullable=True),
        sa.Column("payment_date", sa.Date(), nullable=True),
        sa.Column("bank_name", sa.String(length=120), nullable=True),
        sa.Column("proof_file_path", sa.String(length=500), nullable=False),
        sa.Column("ocr_provider", sa.String(length=50), nullable=False),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("rejection_reason", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["bike_race_id"], ["bike_races.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["competition_biker_id"], ["competition_bikers.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("id_transaction", name="uq_race_qr_payments_id_transaction"),
    )
    op.create_index("ix_race_qr_payments_bike_race_id", "race_qr_payments", ["bike_race_id"])
    op.create_index("ix_race_qr_payments_competition_biker_id", "race_qr_payments", ["competition_biker_id"])
    op.create_index("ix_race_qr_payments_status", "race_qr_payments", ["status"])


def downgrade() -> None:
    op.drop_index("ix_race_qr_payments_status", table_name="race_qr_payments")
    op.drop_index("ix_race_qr_payments_competition_biker_id", table_name="race_qr_payments")
    op.drop_index("ix_race_qr_payments_bike_race_id", table_name="race_qr_payments")
    op.drop_table("race_qr_payments")
