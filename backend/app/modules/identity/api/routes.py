from app.modules.identity.api.dependencies import (
    AuthenticationServiceDependency,
    CurrentUserDependency,
)
from app.modules.identity.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    MembershipNotFoundError,
)
from app.modules.identity.schemas import (
    CurrentUserContext,
    LoginRequest,
    LoginResponse,
)
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest,
    authentication_service: AuthenticationServiceDependency,
) -> LoginResponse:
    """Authenticate a user and issue an organization-scoped access token."""

    try:
        context = await authentication_service.authenticate(
            email=request.email,
            password=request.password,
        )
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    except InactiveUserError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user account is inactive.",
        ) from error
    except MembershipNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active organization membership was found.",
        ) from error

    return LoginResponse(
        access_token=context.access_token,
        user_id=context.user_id,
        membership_id=context.membership_id,
        organization_id=context.organization_id,
        email=context.email,
        role_ids=context.role_ids,
    )


@router.get(
    "/me",
    response_model=CurrentUserContext,
)
async def get_me(
    current_user: CurrentUserDependency,
) -> CurrentUserContext:
    """Return the organization-scoped context from the access token."""

    return current_user
