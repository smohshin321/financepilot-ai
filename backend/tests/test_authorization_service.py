from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.modules.identity.exceptions import AuthorizationDeniedError
from app.modules.identity.services import AuthorizationService


def build_service() -> tuple[AuthorizationService, AsyncMock]:
    permission_repository = AsyncMock()

    service = AuthorizationService(
        permission_repository=permission_repository,
    )

    return service, permission_repository


@pytest.mark.asyncio
async def test_list_permissions_returns_repository_values() -> None:
    service, repository = build_service()
    membership_id = uuid4()

    repository.list_codes_for_membership.return_value = {
        "budget.read",
        "forecast.edit",
    }

    permissions = await service.list_permissions(membership_id)

    assert permissions == {
        "budget.read",
        "forecast.edit",
    }

    repository.list_codes_for_membership.assert_awaited_once_with(membership_id)


@pytest.mark.asyncio
async def test_has_permission_returns_true() -> None:
    service, repository = build_service()
    membership_id = uuid4()

    repository.list_codes_for_membership.return_value = {
        "budget.read",
    }

    result = await service.has_permission(
        membership_id=membership_id,
        permission_code="budget.read",
    )

    assert result is True


@pytest.mark.asyncio
async def test_has_permission_returns_false() -> None:
    service, repository = build_service()
    membership_id = uuid4()

    repository.list_codes_for_membership.return_value = {
        "budget.read",
    }

    result = await service.has_permission(
        membership_id=membership_id,
        permission_code="budget.edit",
    )

    assert result is False


@pytest.mark.asyncio
async def test_require_permission_allows_authorized_membership() -> None:
    service, repository = build_service()
    membership_id = uuid4()

    repository.list_codes_for_membership.return_value = {
        "forecast.edit",
    }

    await service.require_permission(
        membership_id=membership_id,
        permission_code="forecast.edit",
    )


@pytest.mark.asyncio
async def test_require_permission_rejects_unauthorized_membership() -> None:
    service, repository = build_service()
    membership_id = uuid4()

    repository.list_codes_for_membership.return_value = {
        "forecast.read",
    }

    with pytest.raises(AuthorizationDeniedError):
        await service.require_permission(
            membership_id=membership_id,
            permission_code="forecast.edit",
        )
