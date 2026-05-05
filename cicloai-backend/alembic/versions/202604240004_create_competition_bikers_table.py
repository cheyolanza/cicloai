"""create competition bikers table

Revision ID: 202604240004
Revises: 202604240003
Create Date: 2026-04-24 00:04:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202604240004"
down_revision: str | None = "202604240003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "competition_bikers",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("race_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("dni", sa.String(length=7), nullable=False),
        sa.Column("dni_extension", sa.String(length=2), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("requested_category", sa.String(length=30), nullable=False),
        sa.Column("detected_category", sa.String(length=30), nullable=False),
        sa.Column("bike_team_name", sa.String(length=100), nullable=False),
        sa.Column("payment_status", sa.String(length=30), nullable=False),
        sa.Column("payment_reference", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["race_id"], ["bike_races.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint(
            "race_id",
            "dni",
            "dni_extension",
            name="uq_competition_bikers_race_identity",
        ),
    )
    op.create_index("ix_competition_bikers_dni", "competition_bikers", ["dni"])
    op.create_index("ix_competition_bikers_race_id", "competition_bikers", ["race_id"])
    op.create_index("ix_competition_bikers_status", "competition_bikers", ["status"])


def downgrade() -> None:
    op.drop_index("ix_competition_bikers_status", table_name="competition_bikers")
    op.drop_index("ix_competition_bikers_race_id", table_name="competition_bikers")
    op.drop_index("ix_competition_bikers_dni", table_name="competition_bikers")
    op.drop_table("competition_bikers")
