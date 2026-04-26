"""add cost to bike races

Revision ID: 202604240007
Revises: 202604240006
Create Date: 2026-04-24 00:07:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202604240007"
down_revision: str | None = "202604240006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "bike_races",
        sa.Column("cost", sa.Numeric(10, 2), nullable=False, server_default="0"),
    )
    op.execute("UPDATE bike_races SET cost = race_cost WHERE cost = 0")
    op.alter_column("bike_races", "cost", server_default=None)


def downgrade() -> None:
    op.drop_column("bike_races", "cost")
