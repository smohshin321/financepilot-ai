from datetime import date
from uuid import UUID

from app.modules.planning.models import PlanningStatus, PlanningType
from pydantic import BaseModel, ConfigDict, Field


class PlanningCycleCreate(BaseModel):
    """Request schema for creating a planning cycle."""

    name: str = Field(
        min_length=1,
        max_length=150,
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    planning_type: PlanningType
    fiscal_year: int = Field(
        ge=2000,
        le=2200,
    )
    start_date: date
    end_date: date


class PlanningCycleResponse(BaseModel):
    """Response schema for a planning cycle."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    planning_type: PlanningType
    fiscal_year: int
    start_date: date
    end_date: date
    status: PlanningStatus
    is_active: bool
