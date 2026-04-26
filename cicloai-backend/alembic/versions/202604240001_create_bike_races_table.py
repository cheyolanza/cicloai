"""create bike races table

Revision ID: 202604240001
Revises:
Create Date: 2026-04-24 00:01:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202604240001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bike_races",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("location_name", sa.String(length=150), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("date_of_race", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_bike_races_name", "bike_races", ["name"])
    op.create_index("ix_bike_races_status", "bike_races", ["status"])
    op.create_index("ix_bike_races_year", "bike_races", ["year"])
    op.create_check_constraint("ck_bike_races_status", "bike_races", "status in ('active', 'deactive')")
    op.create_unique_constraint("uq_bike_races_name_year", "bike_races", ["name", "year"])


def downgrade() -> None:
    op.drop_constraint("uq_bike_races_name_year", "bike_races", type_="unique")
    op.drop_constraint("ck_bike_races_status", "bike_races", type_="check")
    op.drop_index("ix_bike_races_year", table_name="bike_races")
    op.drop_index("ix_bike_races_status", table_name="bike_races")
    op.drop_index("ix_bike_races_name", table_name="bike_races")
    op.drop_table("bike_races")
