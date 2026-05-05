"""add born to to categories

Revision ID: 202604280006
Revises: 202604280005
Create Date: 2026-04-30 00:06:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202604280006"
down_revision: str | None = "202604280005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "categories",
        sa.Column("born_to", sa.Integer(), nullable=False, server_default="2026"),
    )
    op.alter_column("categories", "born_to", server_default=None)


def downgrade() -> None:
    op.drop_column("categories", "born_to")
