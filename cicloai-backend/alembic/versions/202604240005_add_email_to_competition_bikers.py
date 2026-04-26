"""add email to competition bikers

Revision ID: 202604240005
Revises: 202604240004
Create Date: 2026-04-24 00:05:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202604240005"
down_revision: str | None = "202604240004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "competition_bikers",
        sa.Column("email", sa.String(length=254), nullable=False, server_default="pending-email@cicloai.local"),
    )
    op.alter_column("competition_bikers", "email", server_default=None)


def downgrade() -> None:
    op.drop_column("competition_bikers", "email")
