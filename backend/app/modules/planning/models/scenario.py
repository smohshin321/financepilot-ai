from typing import TYPE_CHECKING
from uuid import UUID

from app.shared.constants import DESCRIPTION_MAX_LENGTH
from app.shared.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.planning.models.budget_version import BudgetVersion
    from app.modules.planning.models.planning_cycle import PlanningCycle


class Scenario(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents a planning assumption set within a planning cycle."""

    __tablename__ = "scenarios"

    __table_args__ = (
        Index(
            "ix_scenarios_planning_cycle_code",
            "planning_cycle_id",
            "code",
            unique=True,
        ),
        Index(
            "ix_scenarios_planning_cycle_default",
            "planning_cycle_id",
            "is_default",
        ),
    )

    planning_cycle_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "planning_cycles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    planning_cycle: Mapped["PlanningCycle"] = relationship(
        back_populates="scenarios",
        lazy="selectin",
    )
    budget_versions: Mapped[list["BudgetVersion"]] = relationship(
        back_populates="scenario",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
