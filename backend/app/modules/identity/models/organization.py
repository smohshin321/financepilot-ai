from typing import TYPE_CHECKING

from app.modules.identity.models.enums import OrganizationStatus
from app.shared.constants import (
    CURRENCY_CODE_LENGTH,
    DEFAULT_FISCAL_YEAR_START_MONTH,
    DISPLAY_NAME_MAX_LENGTH,
    LEGAL_NAME_MAX_LENGTH,
    ORGANIZATION_CODE_MAX_LENGTH,
    TIMEZONE_MAX_LENGTH,
)
from app.shared.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import CheckConstraint, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.identity.models.membership import Membership


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Tenant root for FinancePilot AI planning and reporting data."""

    __tablename__ = "organizations"

    __table_args__ = (
        CheckConstraint(
            "fiscal_year_start_month BETWEEN 1 AND 12",
            name="fiscal_year_start_month_range",
        ),
        Index("ix_organizations_status", "status"),
    )

    code: Mapped[str] = mapped_column(
        String(ORGANIZATION_CODE_MAX_LENGTH),
        nullable=False,
        unique=True,
    )

    legal_name: Mapped[str] = mapped_column(
        String(LEGAL_NAME_MAX_LENGTH),
        nullable=False,
        unique=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(DISPLAY_NAME_MAX_LENGTH),
        nullable=False,
    )

    base_currency: Mapped[str] = mapped_column(
        String(CURRENCY_CODE_LENGTH),
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String(TIMEZONE_MAX_LENGTH),
        nullable=False,
    )

    fiscal_year_start_month: Mapped[int] = mapped_column(
        nullable=False,
        default=DEFAULT_FISCAL_YEAR_START_MONTH,
        server_default=str(DEFAULT_FISCAL_YEAR_START_MONTH),
    )

    status: Mapped[OrganizationStatus] = mapped_column(
        Enum(
            OrganizationStatus,
            name="organization_status",
            native_enum=True,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
        default=OrganizationStatus.ACTIVE,
        server_default=OrganizationStatus.ACTIVE.value,
    )

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
