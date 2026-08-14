from datetime import date
from uuid import uuid4

import pytest
from app.modules.planning.models import PlanningStatus, PlanningType
from app.modules.planning.schemas import (
    PlanningCycleCreate,
    PlanningCycleResponse,
)
from pydantic import ValidationError


def test_planning_cycle_create_accepts_valid_payload() -> None:
    payload = PlanningCycleCreate(
        name="FY2027 Budget",
        description="Annual operating plan",
        planning_type=PlanningType.BUDGET,
        fiscal_year=2027,
        start_date=date(2027, 1, 1),
        end_date=date(2027, 12, 31),
    )

    assert payload.name == "FY2027 Budget"
    assert payload.description == "Annual operating plan"
    assert payload.planning_type is PlanningType.BUDGET
    assert payload.fiscal_year == 2027


def test_planning_cycle_create_description_is_optional() -> None:
    payload = PlanningCycleCreate(
        name="FY2027 Forecast",
        planning_type=PlanningType.FORECAST,
        fiscal_year=2027,
        start_date=date(2027, 1, 1),
        end_date=date(2027, 12, 31),
    )

    assert payload.description is None


@pytest.mark.parametrize(
    "fiscal_year",
    [1999, 2201],
)
def test_planning_cycle_create_rejects_invalid_fiscal_year(
    fiscal_year: int,
) -> None:
    with pytest.raises(ValidationError):
        PlanningCycleCreate(
            name="Invalid Cycle",
            planning_type=PlanningType.BUDGET,
            fiscal_year=fiscal_year,
            start_date=date(2027, 1, 1),
            end_date=date(2027, 12, 31),
        )


def test_planning_cycle_create_rejects_empty_name() -> None:
    with pytest.raises(ValidationError):
        PlanningCycleCreate(
            name="",
            planning_type=PlanningType.BUDGET,
            fiscal_year=2027,
            start_date=date(2027, 1, 1),
            end_date=date(2027, 12, 31),
        )


def test_planning_cycle_response_supports_attribute_mapping() -> None:
    organization_id = uuid4()
    planning_cycle_id = uuid4()

    class PlanningCycleObject:
        pass

    obj = PlanningCycleObject()
    obj.id = planning_cycle_id
    obj.organization_id = organization_id
    obj.name = "FY2027 Budget"
    obj.description = None
    obj.planning_type = PlanningType.BUDGET
    obj.fiscal_year = 2027
    obj.start_date = date(2027, 1, 1)
    obj.end_date = date(2027, 12, 31)
    obj.status = PlanningStatus.DRAFT
    obj.is_active = True

    response = PlanningCycleResponse.model_validate(obj)

    assert response.id == planning_cycle_id
    assert response.organization_id == organization_id
    assert response.status is PlanningStatus.DRAFT
    assert response.is_active is True
