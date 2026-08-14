from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BudgetLineCreate(BaseModel):
    """Request schema for creating a budget line."""

    account_id: UUID | None = None
    department_id: UUID | None = None
    cost_center_id: UUID | None = None

    period: int = Field(
        ge=1,
        le=12,
    )

    amount: Decimal = Field(
        ge=Decimal("0"),
    )

    currency: str = Field(
        min_length=3,
        max_length=3,
    )

    notes: str | None = Field(
        default=None,
        max_length=500,
    )


class BudgetLineUpdate(BaseModel):
    """Request schema for updating a budget line."""

    account_id: UUID | None = None
    department_id: UUID | None = None
    cost_center_id: UUID | None = None

    period: int = Field(
        ge=1,
        le=12,
    )

    amount: Decimal = Field(
        ge=Decimal("0"),
    )

    currency: str = Field(
        min_length=3,
        max_length=3,
    )

    notes: str | None = Field(
        default=None,
        max_length=500,
    )


class BudgetLineResponse(BaseModel):
    """Response schema for a budget line."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    budget_version_id: UUID
    account_id: UUID | None
    department_id: UUID | None
    cost_center_id: UUID | None
    period: int
    amount: Decimal
    currency: str
    notes: str | None
