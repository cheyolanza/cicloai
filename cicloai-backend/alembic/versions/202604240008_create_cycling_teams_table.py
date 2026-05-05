"""create cycling teams table

Revision ID: 202604240008
Revises: 202604240007
Create Date: 2026-04-24 00:08:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202604240008"
down_revision: str | None = "202604240007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cycling_teams",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
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
    )
    op.create_index("ix_cycling_teams_name", "cycling_teams", ["name"])
    op.create_index("ix_cycling_teams_status", "cycling_teams", ["status"])
    op.create_unique_constraint("uq_cycling_teams_name", "cycling_teams", ["name"])


def downgrade() -> None:
    op.drop_constraint("uq_cycling_teams_name", "cycling_teams", type_="unique")
    op.drop_index("ix_cycling_teams_status", table_name="cycling_teams")
    op.drop_index("ix_cycling_teams_name", table_name="cycling_teams")
    op.drop_table("cycling_teams")
