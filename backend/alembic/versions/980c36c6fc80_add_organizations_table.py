"""Add organizations table.

Revision ID: 980c36c6fc80
Revises: 20260724_0001
Create Date: 2026-07-26 04:11:19.762333+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "980c36c6fc80"
down_revision: str | None = "20260724_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


organization_status = sa.Enum(
    "active",
    "inactive",
    "suspended",
    name="organization_status",
)


def upgrade() -> None:
    """Create the organizations table."""

    op.create_table(
        "organizations",
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column(
            "fiscal_year_start_month",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
        sa.Column(
            "status",
            organization_status,
            server_default="active",
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "fiscal_year_start_month BETWEEN 1 AND 12",
            name=op.f("ck_organizations_fiscal_year_start_month_range"),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_organizations"),
        ),
        sa.UniqueConstraint(
            "code",
            name=op.f("uq_organizations_code"),
        ),
        sa.UniqueConstraint(
            "legal_name",
            name=op.f("uq_organizations_legal_name"),
        ),
    )

    op.create_index(
        "ix_organizations_status",
        "organizations",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the organizations table and its PostgreSQL enum."""

    op.drop_index(
        "ix_organizations_status",
        table_name="organizations",
    )
    op.drop_table("organizations")

    organization_status.drop(
        op.get_bind(),
        checkfirst=True,
    )
