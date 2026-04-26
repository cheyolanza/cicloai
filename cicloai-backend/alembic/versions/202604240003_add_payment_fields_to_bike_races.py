"""add payment fields to bike races

Revision ID: 202604240003
Revises: 202604240002
Create Date: 2026-04-24 00:03:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202604240003"
down_revision: str | None = "202604240002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("bike_races", sa.Column("race_cost", sa.Integer(), nullable=False, server_default="60"))
    op.add_column("bike_races", sa.Column("currency", sa.String(length=3), nullable=False, server_default="BOB"))
    op.add_column("bike_races", sa.Column("payment_qr_image", sa.LargeBinary(), nullable=True))
    op.alter_column("bike_races", "race_cost", server_default=None)
    op.alter_column("bike_races", "currency", server_default=None)


def downgrade() -> None:
    op.drop_column("bike_races", "payment_qr_image")
    op.drop_column("bike_races", "currency")
    op.drop_column("bike_races", "race_cost")
