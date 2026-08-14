from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScenarioCreate(BaseModel):
    """Request schema for creating a planning scenario."""

    code: str = Field(
        min_length=1,
        max_length=100,
    )
    name: str = Field(
        min_length=1,
        max_length=150,
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    is_default: bool = False


class ScenarioResponse(BaseModel):
    """Response schema for a planning scenario."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    planning_cycle_id: UUID
    code: str
    name: str
    description: str | None
    is_default: bool
    is_active: bool
