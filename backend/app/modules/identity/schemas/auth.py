from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Credentials submitted to the login endpoint."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class LoginResponse(BaseModel):
    """Access token and authenticated organization context."""

    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    membership_id: UUID
    organization_id: UUID
    email: str
    role_ids: list[UUID]


class AuthenticatedUserContext(BaseModel):
    """Organization-scoped identity returned after authentication."""

    user_id: UUID
    membership_id: UUID
    organization_id: UUID
    email: str
    role_ids: list[UUID]
    access_token: str


class CurrentUserContext(BaseModel):
    """Identity context resolved from a valid access token."""

    user_id: UUID
    membership_id: UUID
    organization_id: UUID
    role_ids: list[UUID]
