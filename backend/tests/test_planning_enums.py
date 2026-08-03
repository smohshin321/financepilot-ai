from app.modules.planning.models import PlanningStatus, PlanningType


def test_planning_type_values() -> None:
    assert PlanningType.BUDGET.value == "budget"
    assert PlanningType.FORECAST.value == "forecast"
    assert PlanningType.ROLLING_FORECAST.value == "rolling_forecast"
    assert PlanningType.LONG_RANGE_PLAN.value == "long_range_plan"


def test_planning_status_values() -> None:
    assert PlanningStatus.DRAFT.value == "draft"
    assert PlanningStatus.ACTIVE.value == "active"
    assert PlanningStatus.CLOSED.value == "closed"
    assert PlanningStatus.ARCHIVED.value == "archived"


def test_planning_enums_are_string_compatible() -> None:
    assert str(PlanningType.BUDGET) == "budget"
    assert str(PlanningStatus.DRAFT) == "draft"
