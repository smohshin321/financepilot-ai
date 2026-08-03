from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from app.shared.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.planning.models.budget_version import BudgetVersion


class BudgetLine(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents a single periodic financial planning value."""

    __tablename__ = "budget_lines"

    __table_args__ = (
        CheckConstraint(
            "period BETWEEN 1 AND 12",
            name="period_range",
        ),
        Index(
            "ix_budget_lines_version_period",
            "budget_version_id",
            "period",
        ),
        Index(
            "ix_budget_lines_version_dimensions",
            "budget_version_id",
            "account_id",
            "department_id",
            "cost_center_id",
        ),
    )

    budget_version_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "budget_versions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    account_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
    )

    department_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
    )

    cost_center_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
    )

    period: Mapped[int] = mapped_column(
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=4),
        nullable=False,
        default=Decimal("0"),
        server_default="0",
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    budget_version: Mapped["BudgetVersion"] = relationship(
        back_populates="budget_lines",
        lazy="selectin",
    )
