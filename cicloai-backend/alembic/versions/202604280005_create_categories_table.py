"""create categories table

Revision ID: 202604280005
Revises: 202604280004
Create Date: 2026-04-28 00:05:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202604280005"
down_revision: str | None = "202604280004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("sex", sa.String(length=10), nullable=False),
        sa.Column("age_from", sa.Integer(), nullable=False),
        sa.Column("age_to", sa.Integer(), nullable=True),
        sa.Column("born_from", sa.Integer(), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="active"
        ),
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
        sa.UniqueConstraint("name", "sex", name="uq_categories_name_sex"),
    )
    op.create_index("ix_categories_name", "categories", ["name"])
    op.create_index("ix_categories_sex", "categories", ["sex"])
    op.create_index("ix_categories_status", "categories", ["status"])


def downgrade() -> None:
    op.drop_index("ix_categories_status", table_name="categories")
    op.drop_index("ix_categories_sex", table_name="categories")
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")
