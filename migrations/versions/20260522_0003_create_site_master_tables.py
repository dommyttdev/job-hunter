"""create site master tables

Revision ID: 20260522_0003
Revises: 20260521_0002
Create Date: 2026-05-22 00:03:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260522_0003"
down_revision: str | None = "20260521_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "site_region_masters",
        sa.Column("normalized_key", sa.String(length=768), primary_key=True),
        sa.Column("site_id", sa.String(length=64), nullable=False),
        sa.Column("prefecture_code", sa.String(length=255)),
        sa.Column("city_code", sa.String(length=255)),
        sa.Column("region_prefecture", sa.String(length=255), nullable=False),
        sa.Column("region_city", sa.String(length=255)),
    )
    op.create_table(
        "site_occupation_masters",
        sa.Column("normalized_key", sa.String(length=768), primary_key=True),
        sa.Column("site_id", sa.String(length=64), nullable=False),
        sa.Column("job_category_code", sa.String(length=255)),
        sa.Column("job_type_codes", sa.Text(), nullable=False),
        sa.Column("occupation_category", sa.String(length=255), nullable=False),
        sa.Column("occupation_detail", sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("site_occupation_masters")
    op.drop_table("site_region_masters")
