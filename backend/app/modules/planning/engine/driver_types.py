from enum import StrEnum


class DriverType(StrEnum):
    """Supported financial planning driver types."""

    UNIT_VOLUME = "unit_volume"
    UNIT_PRICE = "unit_price"
    GROWTH_RATE = "growth_rate"
    PERCENT_OF_REVENUE = "percent_of_revenue"
    HEADCOUNT = "headcount"
    COST_PER_EMPLOYEE = "cost_per_employee"
    FIXED_AMOUNT = "fixed_amount"
