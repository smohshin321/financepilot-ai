from app.modules.identity.models.enums import OrganizationStatus
from app.shared.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import CheckConstraint, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column


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
        String(30),
        nullable=False,
        unique=True,
    )

    legal_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    base_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    fiscal_year_start_month: Mapped[int] = mapped_column(
        nullable=False,
        default=1,
        server_default="1",
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
