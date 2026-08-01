from typing import TYPE_CHECKING
from uuid import UUID

from app.shared.constants import (
    DESCRIPTION_MAX_LENGTH,
    ROLE_CODE_MAX_LENGTH,
    ROLE_NAME_MAX_LENGTH,
)
from app.shared.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.identity.models.membership_role import MembershipRole
    from app.modules.identity.models.organization import Organization
    from app.modules.identity.models.role_permission import RolePermission


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents an organization-scoped authorization role."""

    __tablename__ = "roles"

    __table_args__ = (
        Index(
            "ix_roles_organization_code",
            "organization_id",
            "code",
            unique=True,
        ),
        Index(
            "ix_roles_organization_active",
            "organization_id",
            "is_active",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(ROLE_CODE_MAX_LENGTH),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(ROLE_NAME_MAX_LENGTH),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )

    is_system: Mapped[bool] = mapped_column(
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

    organization: Mapped["Organization"] = relationship(
        back_populates="roles",
        lazy="selectin",
    )
    membership_roles: Mapped[list["MembershipRole"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
