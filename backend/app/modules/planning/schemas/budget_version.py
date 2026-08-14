from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BudgetVersionCreate(BaseModel):
    """Request schema for creating a budget version."""

    version_number: int = Field(ge=1)
    version_name: str = Field(
        min_length=1,
        max_length=150,
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )


class BudgetVersionResponse(BaseModel):
    """Response schema for a budget version."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scenario_id: UUID
    version_number: int
    version_name: str
    description: str | None
    is_active: bool
    is_locked: bool
