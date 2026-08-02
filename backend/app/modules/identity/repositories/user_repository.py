from uuid import UUID

from app.modules.identity.models import User
from app.modules.identity.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepository):
    """Repository for user persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_email(self, email: str) -> User | None:
        """Return a user by email."""

        result = await self._session.execute(select(User).where(User.email == email))

        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by ID."""

        result = await self._session.execute(select(User).where(User.id == user_id))

        return result.scalar_one_or_none()
