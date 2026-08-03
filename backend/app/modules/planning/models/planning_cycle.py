from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from app.modules.planning.models.enums import PlanningStatus, PlanningType
from app.shared.constants import DESCRIPTION_MAX_LENGTH
from app.shared.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Boolean, CheckConstraint, Date, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.identity.models.organization import Organization
    from app.modules.planning.models.scenario import Scenario


class PlanningCycle(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents an organization-scoped FP&A planning process."""

    __tablename__ = "planning_cycles"

    __table_args__ = (
        CheckConstraint(
            "fiscal_year BETWEEN 2000 AND 2200",
            name="fiscal_year_range",
        ),
        CheckConstraint(
            "end_date >= start_date",
            name="valid_date_range",
        ),
        Index(
            "ix_planning_cycles_organization_fiscal_year",
            "organization_id",
            "fiscal_year",
        ),
        Index(
            "ix_planning_cycles_organization_status",
            "organization_id",
            "status",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
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

    planning_type: Mapped[PlanningType] = mapped_column(
        Enum(
            PlanningType,
            name="planning_type",
            native_enum=True,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
    )

    fiscal_year: Mapped[int] = mapped_column(
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[PlanningStatus] = mapped_column(
        Enum(
            PlanningStatus,
            name="planning_status",
            native_enum=True,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
        default=PlanningStatus.DRAFT,
        server_default=PlanningStatus.DRAFT.value,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    organization: Mapped["Organization"] = relationship(
        lazy="selectin",
    )

    scenarios: Mapped[list["Scenario"]] = relationship(
        back_populates="planning_cycle",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
