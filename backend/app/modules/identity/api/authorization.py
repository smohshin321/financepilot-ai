from collections.abc import Awaitable, Callable
from typing import Annotated

from app.core.database import get_db_session
from app.modules.identity.api.dependencies import CurrentUserDependency
from app.modules.identity.repositories import PermissionRepository
from app.modules.identity.services import AuthorizationService
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


def RequirePermission(
    permission_code: str,
) -> Callable[..., Awaitable[None]]:
    async def dependency(
        current_user: CurrentUserDependency,
        session: Annotated[
            AsyncSession,
            Depends(get_db_session),
        ],
    ) -> None:
        service = AuthorizationService(
            PermissionRepository(session),
        )

        allowed = await service.has_permission(
            membership_id=current_user.membership_id,
            permission_code=permission_code,
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_code}' is required.",
            )

    return dependency
