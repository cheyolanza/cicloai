"""add payment group relations

Revision ID: 202604280004
Revises: 202604280003
Create Date: 2026-04-28 00:04:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202604280004"
down_revision: str | None = "202604280003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "competition_bikers",
        sa.Column("payment_group_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "race_qr_payments",
        sa.Column("payment_group_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_competition_bikers_payment_group_id",
        "competition_bikers",
        ["payment_group_id"],
    )
    op.create_index(
        "ix_race_qr_payments_payment_group_id", "race_qr_payments", ["payment_group_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_race_qr_payments_payment_group_id", table_name="race_qr_payments")
    op.drop_index(
        "ix_competition_bikers_payment_group_id", table_name="competition_bikers"
    )
    op.drop_column("race_qr_payments", "payment_group_id")
    op.drop_column("competition_bikers", "payment_group_id")
