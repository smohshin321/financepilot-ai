from decimal import Decimal

from app.modules.planning.engine.driver import PlanningDriver
from app.modules.planning.engine.exceptions import InvalidDriverValueError


class DriverCalculationEngine:
    """Core driver-based financial calculation engine."""

    @staticmethod
    def revenue(
        *,
        volume: PlanningDriver,
        unit_price: PlanningDriver,
    ) -> Decimal:
        """Calculate revenue from unit volume and unit price."""

        if volume.value < Decimal("0"):
            raise InvalidDriverValueError("Volume cannot be negative.")

        if unit_price.value < Decimal("0"):
            raise InvalidDriverValueError("Unit price cannot be negative.")

        return volume.value * unit_price.value

    @staticmethod
    def apply_growth(
        *,
        base_amount: Decimal,
        growth_rate: PlanningDriver,
    ) -> Decimal:
        """Apply a percentage growth assumption to a base amount."""

        return base_amount * (Decimal("1") + growth_rate.value)

    @staticmethod
    def percent_of_revenue(
        *,
        revenue: Decimal,
        percentage: PlanningDriver,
    ) -> Decimal:
        """Calculate an expense or cost as a percentage of revenue."""

        return revenue * percentage.value

    @staticmethod
    def payroll(
        *,
        headcount: PlanningDriver,
        cost_per_employee: PlanningDriver,
    ) -> Decimal:
        """Calculate payroll from headcount and cost per employee."""

        if headcount.value < Decimal("0"):
            raise InvalidDriverValueError("Headcount cannot be negative.")

        if cost_per_employee.value < Decimal("0"):
            raise InvalidDriverValueError("Cost per employee cannot be negative.")

        return headcount.value * cost_per_employee.value

    @staticmethod
    def fixed_amount(
        *,
        driver: PlanningDriver,
    ) -> Decimal:
        """Return a fixed planning amount."""

        return driver.value
