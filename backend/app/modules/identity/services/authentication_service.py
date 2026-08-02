from app.core.security import create_access_token, verify_password
from app.modules.identity.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    MembershipNotFoundError,
)
from app.modules.identity.repositories import (
    MembershipRepository,
    RoleRepository,
    UserRepository,
)
from app.modules.identity.schemas.auth import AuthenticatedUserContext


class AuthenticationService:
    """Authenticate users and create organization-scoped login contexts."""

    def __init__(
        self,
        user_repository: UserRepository,
        membership_repository: MembershipRepository,
        role_repository: RoleRepository,
    ) -> None:
        self._users = user_repository
        self._memberships = membership_repository
        self._roles = role_repository

    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> AuthenticatedUserContext:
        """Authenticate credentials and issue an organization-scoped access token."""

        normalized_email = email.strip().lower()
        user = await self._users.get_by_email(normalized_email)

        if user is None:
            raise InvalidCredentialsError

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError

        if not user.is_active:
            raise InactiveUserError

        memberships = await self._memberships.list_active_for_user(user.id)

        if not memberships:
            raise MembershipNotFoundError

        # Sprint 3.7 supports the first active organization membership.
        # Explicit organization selection will be added in a later increment.
        membership = memberships[0]

        roles = await self._roles.list_for_membership(membership.id)
        role_ids = [role.id for role in roles]

        access_token = create_access_token(
            user_id=user.id,
            organization_id=membership.organization_id,
            membership_id=membership.id,
            role_ids=role_ids,
        )

        return AuthenticatedUserContext(
            user_id=user.id,
            membership_id=membership.id,
            organization_id=membership.organization_id,
            email=user.email,
            role_ids=role_ids,
            access_token=access_token,
        )
