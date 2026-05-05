"""add strava map html to bike races

Revision ID: 202604280008
Revises: 202604280007
Create Date: 2026-04-30 00:08:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202604280008"
down_revision: str | None = "202604280007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("bike_races", sa.Column("strava_map_html", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("bike_races", "strava_map_html")
