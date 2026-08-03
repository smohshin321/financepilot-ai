from enum import StrEnum


class PlanningType(StrEnum):
    """Supported FinancePilot AI planning processes."""

    BUDGET = "budget"
    FORECAST = "forecast"
    ROLLING_FORECAST = "rolling_forecast"
    LONG_RANGE_PLAN = "long_range_plan"


class PlanningStatus(StrEnum):
    """Lifecycle status of a planning cycle."""

    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"
