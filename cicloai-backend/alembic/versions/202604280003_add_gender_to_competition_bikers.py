"""add gender to competition bikers

Revision ID: 202604280003
Revises: 202604280002
Create Date: 2026-04-28 00:03:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202604280003"
down_revision: str | None = "202604280002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "competition_bikers",
        sa.Column(
            "gender", sa.String(length=10), nullable=False, server_default="hombre"
        ),
    )
    op.create_index(
        op.f("ix_competition_bikers_gender"),
        "competition_bikers",
        ["gender"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_competition_bikers_gender"), table_name="competition_bikers")
    op.drop_column("competition_bikers", "gender")
