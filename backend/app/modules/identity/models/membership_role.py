from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from app.shared.database import Base, UUIDPrimaryKeyMixin
from sqlalchemy import DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.identity.models.membership import Membership
    from app.modules.identity.models.role import Role


class MembershipRole(UUIDPrimaryKeyMixin, Base):
    """Assigns an organization-scoped role to a membership."""

    __tablename__ = "membership_roles"

    __table_args__ = (
        Index(
            "ix_membership_roles_membership_role",
            "membership_id",
            "role_id",
            unique=True,
        ),
    )

    membership_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "memberships.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    role_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    membership: Mapped["Membership"] = relationship(
        back_populates="membership_roles",
        lazy="selectin",
    )

    role: Mapped["Role"] = relationship(
        back_populates="membership_roles",
        lazy="selectin",
    )
