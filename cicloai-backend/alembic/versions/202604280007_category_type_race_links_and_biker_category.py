"""category type race links and biker category

Revision ID: 202604280007
Revises: 202604280006
Create Date: 2026-04-30 00:07:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202604280007"
down_revision: str | None = "202604280006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "categories",
        sa.Column(
            "category_type",
            sa.String(length=20),
            nullable=False,
            server_default="Federado",
        ),
    )
    op.alter_column("categories", "category_type", server_default=None)
    op.create_index("ix_categories_category_type", "categories", ["category_type"])

    op.drop_constraint("uq_categories_name_sex", "categories", type_="unique")
    op.create_unique_constraint(
        "uq_categories_name_sex_type", "categories", ["name", "sex", "category_type"]
    )

    op.create_table(
        "bike_race_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("race_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["race_id"], ["bike_races.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "race_id", "category_id", name="uq_bike_race_categories_pair"
        ),
    )
    op.create_index(
        "ix_bike_race_categories_race_id", "bike_race_categories", ["race_id"]
    )
    op.create_index(
        "ix_bike_race_categories_category_id", "bike_race_categories", ["category_id"]
    )
    _backfill_existing_race_categories()

    op.add_column(
        "competition_bikers",
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_competition_bikers_category_id", "competition_bikers", ["category_id"]
    )
    op.create_foreign_key(
        "fk_competition_bikers_category_id_categories",
        "competition_bikers",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_competition_bikers_category_id_categories",
        "competition_bikers",
        type_="foreignkey",
    )
    op.drop_index("ix_competition_bikers_category_id", table_name="competition_bikers")
    op.drop_column("competition_bikers", "category_id")

    op.drop_index(
        "ix_bike_race_categories_category_id", table_name="bike_race_categories"
    )
    op.drop_index("ix_bike_race_categories_race_id", table_name="bike_race_categories")
    op.drop_table("bike_race_categories")

    op.drop_constraint("uq_categories_name_sex_type", "categories", type_="unique")
    op.create_unique_constraint("uq_categories_name_sex", "categories", ["name", "sex"])
    op.drop_index("ix_categories_category_type", table_name="categories")
    op.drop_column("categories", "category_type")


def _backfill_existing_race_categories() -> None:
    bind = op.get_bind()
    races = bind.execute(sa.text("SELECT id FROM bike_races")).fetchall()
    categories = bind.execute(sa.text("SELECT id FROM categories")).fetchall()
    if not races or not categories:
        return

    rows = [
        {"id": str(uuid4()), "race_id": str(race.id), "category_id": str(category.id)}
        for race in races
        for category in categories
    ]
    bind.execute(
        sa.text(
            """
            INSERT INTO bike_race_categories (id, race_id, category_id)
            VALUES (:id, :race_id, :category_id)
            ON CONFLICT (race_id, category_id) DO NOTHING
            """
        ),
        rows,
    )
