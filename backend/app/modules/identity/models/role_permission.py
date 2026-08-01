from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from app.shared.database import Base, UUIDPrimaryKeyMixin
from sqlalchemy import DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.identity.models.permission import Permission
    from app.modules.identity.models.role import Role


class RolePermission(UUIDPrimaryKeyMixin, Base):
    """Assigns a permission to a role."""

    __tablename__ = "role_permissions"

    __table_args__ = (
        Index(
            "ix_role_permissions_role_permission",
            "role_id",
            "permission_id",
            unique=True,
        ),
    )

    role_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    permission_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "permissions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    role: Mapped["Role"] = relationship(
        back_populates="role_permissions",
        lazy="selectin",
    )

    permission: Mapped["Permission"] = relationship(
        back_populates="role_permissions",
        lazy="selectin",
    )
