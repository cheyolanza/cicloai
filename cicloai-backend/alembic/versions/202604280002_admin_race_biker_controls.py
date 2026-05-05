"""admin race biker controls

Revision ID: 202604280002
Revises: 202604280001
Create Date: 2026-04-28 00:02:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202604280002"
down_revision: str | None = "202604280001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE competition_bikers
        SET status = CASE
            WHEN payment_status = 'pending_bulk_payment' THEN 'pendiente'
            ELSE 'habilitado'
        END
        WHERE status = 'registered'
        """
    )
    op.create_index(
        "uq_bike_races_single_active",
        "bike_races",
        ["status"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    op.drop_index("uq_bike_races_single_active", table_name="bike_races")
