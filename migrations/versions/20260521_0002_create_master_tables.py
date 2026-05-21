"""create master tables

Revision ID: 20260521_0002
Revises: 20260521_0001
Create Date: 2026-05-21 00:02:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260521_0002"
down_revision: str | None = "20260521_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "regions",
        sa.Column("normalized_key", sa.String(length=512), primary_key=True),
        sa.Column("prefecture", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=255)),
    )
    op.create_table(
        "occupations",
        sa.Column("normalized_key", sa.String(length=512), primary_key=True),
        sa.Column("category", sa.String(length=255), nullable=False),
        sa.Column("detail", sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("occupations")
    op.drop_table("regions")
