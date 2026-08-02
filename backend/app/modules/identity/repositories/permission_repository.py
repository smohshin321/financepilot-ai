from uuid import UUID

from app.modules.identity.models import (
    MembershipRole,
    Permission,
    RolePermission,
)
from app.modules.identity.repositories.base import BaseRepository
from sqlalchemy import select


class PermissionRepository(BaseRepository):
    """Repository for resolving effective membership permissions."""

    async def list_codes_for_membership(
        self,
        membership_id: UUID,
    ) -> set[str]:
        """Return unique permission codes assigned to a membership."""

        result = await self._session.execute(
            select(Permission.code)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .join(
                MembershipRole,
                MembershipRole.role_id == RolePermission.role_id,
            )
            .where(
                MembershipRole.membership_id == membership_id,
            )
        )

        return set(result.scalars().all())
