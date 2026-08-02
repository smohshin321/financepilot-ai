from typing import Annotated
from uuid import UUID

import jwt
from app.core.database import get_db_session
from app.core.security import decode_access_token
from app.modules.identity.repositories import (
    MembershipRepository,
    RoleRepository,
    UserRepository,
)
from app.modules.identity.schemas import CurrentUserContext
from app.modules.identity.services import AuthenticationService
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

bearer_scheme = HTTPBearer(auto_error=False)


def get_authentication_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthenticationService:
    """Build the authentication service for the current request."""

    return AuthenticationService(
        user_repository=UserRepository(session),
        membership_repository=MembershipRepository(session),
        role_repository=RoleRepository(session),
    )


def unauthorized_exception() -> HTTPException:
    """Return the standard authentication failure response."""

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def parse_uuid_claim(payload: dict[str, object], claim: str) -> UUID:
    """Parse a required UUID claim from a JWT payload."""

    value = payload.get(claim)

    if not isinstance(value, str):
        raise unauthorized_exception()

    try:
        return UUID(value)
    except ValueError as error:
        raise unauthorized_exception() from error


async def get_current_user_context(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> CurrentUserContext:
    """Resolve the organization-scoped identity from a bearer token."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized_exception()

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError as error:
        raise unauthorized_exception() from error

    role_values = payload.get("role_ids")

    if not isinstance(role_values, list) or not all(
        isinstance(role_id, str) for role_id in role_values
    ):
        raise unauthorized_exception()

    try:
        role_ids = [UUID(role_id) for role_id in role_values]
    except ValueError as error:
        raise unauthorized_exception() from error

    return CurrentUserContext(
        user_id=parse_uuid_claim(payload, "sub"),
        membership_id=parse_uuid_claim(payload, "membership_id"),
        organization_id=parse_uuid_claim(payload, "org"),
        role_ids=role_ids,
    )


AuthenticationServiceDependency = Annotated[
    AuthenticationService,
    Depends(get_authentication_service),
]

CurrentUserDependency = Annotated[
    CurrentUserContext,
    Depends(get_current_user_context),
]
