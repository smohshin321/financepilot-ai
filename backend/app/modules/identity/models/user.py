from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.identity.models.membership import Membership

from app.shared.constants import (
    EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PASSWORD_HASH_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)
from app.shared.database import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents an authenticated FinancePilot AI user."""

    __tablename__ = "users"

    __table_args__ = (Index("ix_users_email", "email"),)

    email: Mapped[str] = mapped_column(
        String(EMAIL_MAX_LENGTH),
        nullable=False,
        unique=True,
    )

    username: Mapped[str | None] = mapped_column(
        String(USERNAME_MAX_LENGTH),
        nullable=True,
        unique=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(NAME_MAX_LENGTH),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(NAME_MAX_LENGTH),
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(PASSWORD_HASH_MAX_LENGTH),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
