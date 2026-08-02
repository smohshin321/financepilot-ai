from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.core.security import decode_access_token, hash_password
from app.modules.identity.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    MembershipNotFoundError,
)
from app.modules.identity.models import Membership, Role, User
from app.modules.identity.services import AuthenticationService


def build_service() -> tuple[
    AuthenticationService,
    AsyncMock,
    AsyncMock,
    AsyncMock,
]:
    user_repository = AsyncMock()
    membership_repository = AsyncMock()
    role_repository = AsyncMock()

    service = AuthenticationService(
        user_repository=user_repository,
        membership_repository=membership_repository,
        role_repository=role_repository,
    )

    return (
        service,
        user_repository,
        membership_repository,
        role_repository,
    )


@pytest.mark.asyncio
async def test_authenticate_returns_user_context() -> None:
    service, users, memberships, roles = build_service()

    user = User(
        id=uuid4(),
        email="analyst@financepilot.ai",
        first_name="Finance",
        last_name="Analyst",
        hashed_password=hash_password("SecurePassword123!"),
        is_active=True,
        is_superuser=False,
        email_verified=True,
    )

    membership = Membership(
        id=uuid4(),
        user_id=user.id,
        organization_id=uuid4(),
        is_active=True,
        joined_at=datetime.now(UTC),
    )

    assigned_roles = [
        Role(
            id=uuid4(),
            organization_id=membership.organization_id,
            code="fpa_manager",
            name="FP&A Manager",
            is_system=True,
            is_active=True,
        ),
        Role(
            id=uuid4(),
            organization_id=membership.organization_id,
            code="viewer",
            name="Viewer",
            is_system=True,
            is_active=True,
        ),
    ]

    users.get_by_email.return_value = user
    memberships.list_active_for_user.return_value = [membership]
    roles.list_for_membership.return_value = assigned_roles

    context = await service.authenticate(
        email="  ANALYST@FINANCEPILOT.AI ",
        password="SecurePassword123!",
    )

    assert context.user_id == user.id
    assert context.membership_id == membership.id
    assert context.organization_id == membership.organization_id
    assert context.email == user.email
    assert context.role_ids == [role.id for role in assigned_roles]

    payload = decode_access_token(context.access_token)

    assert payload["sub"] == str(user.id)
    assert payload["org"] == str(membership.organization_id)
    assert payload["membership_id"] == str(membership.id)
    assert payload["role_ids"] == [str(role.id) for role in assigned_roles]

    users.get_by_email.assert_awaited_once_with("analyst@financepilot.ai")
    memberships.list_active_for_user.assert_awaited_once_with(user.id)
    roles.list_for_membership.assert_awaited_once_with(membership.id)


@pytest.mark.asyncio
async def test_authenticate_rejects_unknown_user() -> None:
    service, users, memberships, roles = build_service()
    users.get_by_email.return_value = None

    with pytest.raises(InvalidCredentialsError):
        await service.authenticate(
            email="missing@financepilot.ai",
            password="SecurePassword123!",
        )

    memberships.list_active_for_user.assert_not_awaited()
    roles.list_for_membership.assert_not_awaited()


@pytest.mark.asyncio
async def test_authenticate_rejects_invalid_password() -> None:
    service, users, memberships, roles = build_service()

    user = User(
        id=uuid4(),
        email="analyst@financepilot.ai",
        first_name="Finance",
        last_name="Analyst",
        hashed_password=hash_password("CorrectPassword123!"),
        is_active=True,
        is_superuser=False,
        email_verified=True,
    )
    users.get_by_email.return_value = user

    with pytest.raises(InvalidCredentialsError):
        await service.authenticate(
            email=user.email,
            password="WrongPassword",
        )

    memberships.list_active_for_user.assert_not_awaited()
    roles.list_for_membership.assert_not_awaited()


@pytest.mark.asyncio
async def test_authenticate_rejects_inactive_user() -> None:
    service, users, memberships, roles = build_service()

    user = User(
        id=uuid4(),
        email="inactive@financepilot.ai",
        first_name="Inactive",
        last_name="User",
        hashed_password=hash_password("SecurePassword123!"),
        is_active=False,
        is_superuser=False,
        email_verified=True,
    )
    users.get_by_email.return_value = user

    with pytest.raises(InactiveUserError):
        await service.authenticate(
            email=user.email,
            password="SecurePassword123!",
        )

    memberships.list_active_for_user.assert_not_awaited()
    roles.list_for_membership.assert_not_awaited()


@pytest.mark.asyncio
async def test_authenticate_requires_active_membership() -> None:
    service, users, memberships, roles = build_service()

    user = User(
        id=uuid4(),
        email="nomembership@financepilot.ai",
        first_name="No",
        last_name="Membership",
        hashed_password=hash_password("SecurePassword123!"),
        is_active=True,
        is_superuser=False,
        email_verified=True,
    )

    users.get_by_email.return_value = user
    memberships.list_active_for_user.return_value = []

    with pytest.raises(MembershipNotFoundError):
        await service.authenticate(
            email=user.email,
            password="SecurePassword123!",
        )

    roles.list_for_membership.assert_not_awaited()
