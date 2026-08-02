from uuid import UUID

from app.modules.identity.models import Membership, MembershipRole
from app.modules.identity.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class MembershipRepository(BaseRepository):
    """Repository for membership persistence."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_active_for_user(
        self,
        user_id: UUID,
    ) -> list[Membership]:
        """Return all active memberships for a user."""

        result = await self._session.execute(
            select(Membership)
            .where(
                Membership.user_id == user_id,
                Membership.is_active.is_(True),
            )
            .options(
                selectinload(Membership.organization),
                selectinload(Membership.membership_roles).selectinload(MembershipRole.role),
            )
        )

        return list(result.scalars().unique().all())
