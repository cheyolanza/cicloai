"""create bike team table

Revision ID: 202604240002
Revises: 202604240001
Create Date: 2026-04-24 00:02:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202604240002"
down_revision: str | None = "202604240001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bike_team",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("manager_name", sa.String(length=120), nullable=True),
        sa.Column("contact_phone", sa.String(length=40), nullable=True),
        sa.Column("facebook_page", sa.String(length=255), nullable=True),
        sa.Column("picture_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_bike_team_active", "bike_team", ["active"])
    op.create_index("ix_bike_team_name", "bike_team", ["name"])
    op.create_unique_constraint("uq_bike_team_name", "bike_team", ["name"])


def downgrade() -> None:
    op.drop_constraint("uq_bike_team_name", "bike_team", type_="unique")
    op.drop_index("ix_bike_team_name", table_name="bike_team")
    op.drop_index("ix_bike_team_active", table_name="bike_team")
    op.drop_table("bike_team")
