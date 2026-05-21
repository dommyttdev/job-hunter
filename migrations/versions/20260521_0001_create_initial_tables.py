"""create initial tables

Revision ID: 20260521_0001
Revises:
Create Date: 2026-05-21 00:01:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260521_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("job_id", sa.String(length=255), primary_key=True),
        sa.Column("site_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("company_name", sa.Text(), nullable=False),
        sa.Column("detail_url", sa.Text(), nullable=False),
        sa.Column("work_location", sa.Text(), nullable=False),
        sa.Column("occupation", sa.Text(), nullable=False),
        sa.Column("salary", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
    )
    op.create_table(
        "job_changes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.String(length=255), nullable=False),
        sa.Column("collection_condition_key", sa.String(length=512), nullable=False),
        sa.Column("change_type", sa.String(length=32), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "subscription_conditions",
        sa.Column("normalized_key", sa.String(length=512), primary_key=True),
        sa.Column("region_prefecture", sa.String(length=255)),
        sa.Column("region_city", sa.String(length=255)),
        sa.Column("occupation_category", sa.String(length=255)),
        sa.Column("occupation_detail", sa.String(length=255)),
    )
    op.create_table(
        "collection_conditions",
        sa.Column("normalized_key", sa.String(length=512), primary_key=True),
        sa.Column("site_id", sa.String(length=64), nullable=False),
        sa.Column("condition_key", sa.String(length=512), nullable=False),
    )
    op.create_table(
        "collection_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("collection_condition_key", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("collected_job_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text()),
    )
    op.create_table(
        "condition_snapshots",
        sa.Column("collection_condition_key", sa.String(length=512), primary_key=True),
        sa.Column(
            "job_id",
            sa.String(length=255),
            sa.ForeignKey("jobs.job_id"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("condition_snapshots")
    op.drop_table("collection_runs")
    op.drop_table("collection_conditions")
    op.drop_table("subscription_conditions")
    op.drop_table("job_changes")
    op.drop_table("jobs")
