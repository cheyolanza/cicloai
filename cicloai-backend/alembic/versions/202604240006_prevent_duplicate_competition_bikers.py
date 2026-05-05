"""prevent duplicate competition bikers

Revision ID: 202604240006
Revises: 202604240005
Create Date: 2026-04-24 00:06:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202604240006"
down_revision: str | None = "202604240005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_competition_bikers_race_dni",
        "competition_bikers",
        ["race_id", "dni"],
    )
    op.create_index(
        "uq_competition_bikers_race_full_name_upper",
        "competition_bikers",
        ["race_id", sa.text("upper(full_name)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_competition_bikers_race_full_name_upper", table_name="competition_bikers"
    )
    op.drop_constraint(
        "uq_competition_bikers_race_dni", "competition_bikers", type_="unique"
    )
