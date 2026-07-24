"""Establish the FinancePilot AI platform migration baseline.

Revision ID: 20260724_0001
Revises:
Create Date: 2026-07-24
"""
from collections.abc import Sequence

revision: str = "20260724_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Establish the initial migration boundary without premature domain tables."""


def downgrade() -> None:
    """Remove the initial migration boundary."""
