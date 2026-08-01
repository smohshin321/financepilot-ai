from typing import TYPE_CHECKING

from app.shared.constants import (
    DESCRIPTION_MAX_LENGTH,
    PERMISSION_CODE_MAX_LENGTH,
    PERMISSION_NAME_MAX_LENGTH,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.identity.models.role_permission import RolePermission

from app.shared.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Index, String


class Permission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents a globally available authorization capability."""

    __tablename__ = "permissions"

    __table_args__ = (
        Index(
            "ix_permissions_code",
            "code",
            unique=True,
        ),
    )

    code: Mapped[str] = mapped_column(
        String(PERMISSION_CODE_MAX_LENGTH),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(PERMISSION_NAME_MAX_LENGTH),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(DESCRIPTION_MAX_LENGTH),
        nullable=True,
    )
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
