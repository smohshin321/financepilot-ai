from decimal import Decimal

import pytest
from app.modules.planning.engine import (
    DriverCalculationEngine,
    DriverType,
    InvalidDriverValueError,
    PlanningDriver,
)


def build_driver(
    code: str,
    driver_type: DriverType,
    value: str,
) -> PlanningDriver:
    return PlanningDriver(
        code=code,
        driver_type=driver_type,
        value=Decimal(value),
    )


def test_revenue_calculation() -> None:
    volume = build_driver(
        "sales_volume",
        DriverType.UNIT_VOLUME,
        "1000",
    )
    unit_price = build_driver(
        "average_price",
        DriverType.UNIT_PRICE,
        "25.50",
    )

    result = DriverCalculationEngine.revenue(
        volume=volume,
        unit_price=unit_price,
    )

    assert result == Decimal("25500.00")


def test_growth_calculation() -> None:
    growth_rate = build_driver(
        "revenue_growth",
        DriverType.GROWTH_RATE,
        "0.10",
    )

    result = DriverCalculationEngine.apply_growth(
        base_amount=Decimal("100000"),
        growth_rate=growth_rate,
    )

    assert result == Decimal("110000.00")


def test_percent_of_revenue_calculation() -> None:
    percentage = build_driver(
        "marketing_rate",
        DriverType.PERCENT_OF_REVENUE,
        "0.05",
    )

    result = DriverCalculationEngine.percent_of_revenue(
        revenue=Decimal("500000"),
        percentage=percentage,
    )

    assert result == Decimal("25000.00")


def test_payroll_calculation() -> None:
    headcount = build_driver(
        "headcount",
        DriverType.HEADCOUNT,
        "25",
    )
    cost_per_employee = build_driver(
        "annual_cost",
        DriverType.COST_PER_EMPLOYEE,
        "80000",
    )

    result = DriverCalculationEngine.payroll(
        headcount=headcount,
        cost_per_employee=cost_per_employee,
    )

    assert result == Decimal("2000000")


def test_fixed_amount_calculation() -> None:
    driver = build_driver(
        "office_rent",
        DriverType.FIXED_AMOUNT,
        "15000",
    )

    result = DriverCalculationEngine.fixed_amount(driver=driver)

    assert result == Decimal("15000")


def test_revenue_rejects_negative_volume() -> None:
    volume = build_driver(
        "sales_volume",
        DriverType.UNIT_VOLUME,
        "-10",
    )
    unit_price = build_driver(
        "average_price",
        DriverType.UNIT_PRICE,
        "25",
    )

    with pytest.raises(InvalidDriverValueError):
        DriverCalculationEngine.revenue(
            volume=volume,
            unit_price=unit_price,
        )


def test_payroll_rejects_negative_headcount() -> None:
    headcount = build_driver(
        "headcount",
        DriverType.HEADCOUNT,
        "-1",
    )
    cost_per_employee = build_driver(
        "annual_cost",
        DriverType.COST_PER_EMPLOYEE,
        "80000",
    )

    with pytest.raises(InvalidDriverValueError):
        DriverCalculationEngine.payroll(
            headcount=headcount,
            cost_per_employee=cost_per_employee,
        )
