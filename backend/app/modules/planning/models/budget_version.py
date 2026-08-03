from typing import TYPE_CHECKING
from uuid import UUID

from app.shared.constants import DESCRIPTION_MAX_LENGTH
from app.shared.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.planning.models.budget_line import BudgetLine
    from app.modules.planning.models.scenario import Scenario


class BudgetVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents a controlled version of a planning scenario."""

    __tablename__ = "budget_versions"

    __table_args__ = (
        Index(
            "ix_budget_versions_scenario_number",
            "scenario_id",
            "version_number",
            unique=True,
        ),
        Index(
            "ix_budget_versions_scenario_active",
            "scenario_id",
            "is_active",
        ),
    )

    scenario_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "scenarios.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    version_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    is_locked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    scenario: Mapped["Scenario"] = relationship(
        back_populates="budget_versions",
        lazy="selectin",
    )
    budget_lines: Mapped[list["BudgetLine"]] = relationship(
        back_populates="budget_version",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
