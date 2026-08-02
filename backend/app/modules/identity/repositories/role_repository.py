from uuid import UUID

from app.modules.identity.models import MembershipRole, Role
from app.modules.identity.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class RoleRepository(BaseRepository):
    """Repository for role persistence."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_for_membership(
        self,
        membership_id: UUID,
    ) -> list[Role]:
        """Return all roles assigned to a membership."""

        result = await self._session.execute(
            select(Role)
            .join(
                MembershipRole,
                MembershipRole.role_id == Role.id,
            )
            .where(
                MembershipRole.membership_id == membership_id,
            )
        )

        return list(result.scalars().all())
