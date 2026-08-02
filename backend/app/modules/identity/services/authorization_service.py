from uuid import UUID

from app.modules.identity.exceptions import AuthorizationDeniedError
from app.modules.identity.repositories import PermissionRepository


class AuthorizationService:
    """Resolve and enforce effective membership permissions."""

    def __init__(
        self,
        permission_repository: PermissionRepository,
    ) -> None:
        self._permissions = permission_repository

    async def list_permissions(
        self,
        membership_id: UUID,
    ) -> set[str]:
        """Return all effective permission codes for a membership."""

        return await self._permissions.list_codes_for_membership(membership_id)

    async def has_permission(
        self,
        membership_id: UUID,
        permission_code: str,
    ) -> bool:
        """Return whether a membership has the requested permission."""

        permissions = await self.list_permissions(membership_id)

        return permission_code in permissions

    async def require_permission(
        self,
        membership_id: UUID,
        permission_code: str,
    ) -> None:
        """Raise when a membership lacks the requested permission."""

        if not await self.has_permission(
            membership_id=membership_id,
            permission_code=permission_code,
        ):
            raise AuthorizationDeniedError(permission_code)
