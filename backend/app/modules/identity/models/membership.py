from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from app.shared.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.identity.models.organization import Organization
    from app.modules.identity.models.user import User


class Membership(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Associates a user with an organization."""

    __tablename__ = "memberships"

    __table_args__ = (
        Index(
            "ix_memberships_user_organization",
            "user_id",
            "organization_id",
            unique=True,
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="memberships",
        lazy="selectin",
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="memberships",
        lazy="selectin",
    )
