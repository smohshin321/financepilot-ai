from uuid import UUID

from pydantic import BaseModel


class AuthenticatedUserContext(BaseModel):
    """Organization-scoped identity returned after successful authentication."""

    user_id: UUID
    membership_id: UUID
    organization_id: UUID
    email: str
    role_ids: list[UUID]
    access_token: str
