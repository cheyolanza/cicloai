"""create biker lookup actions table

Revision ID: 202604240009
Revises: 202604240008
Create Date: 2026-04-24 00:09:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202604240009"
down_revision: str | None = "202604240008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "biker_lookup_actions",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "competition_biker_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("bike_race_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("searched_name", sa.String(length=150), nullable=False),
        sa.Column("previous_team_name", sa.String(length=150), nullable=True),
        sa.Column("new_team_name", sa.String(length=150), nullable=True),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["competition_biker_id"], ["competition_bikers.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["bike_race_id"], ["bike_races.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "ix_biker_lookup_actions_competition_biker_id",
        "biker_lookup_actions",
        ["competition_biker_id"],
    )
    op.create_index(
        "ix_biker_lookup_actions_bike_race_id", "biker_lookup_actions", ["bike_race_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_biker_lookup_actions_bike_race_id", table_name="biker_lookup_actions"
    )
    op.drop_index(
        "ix_biker_lookup_actions_competition_biker_id",
        table_name="biker_lookup_actions",
    )
    op.drop_table("biker_lookup_actions")
