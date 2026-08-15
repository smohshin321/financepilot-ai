from decimal import Decimal

from app.modules.planning.engine import (
    ForecastCadence,
    PeriodValue,
    PlanningPeriod,
    PlanningSeries,
    RollingForecastEngine,
    RollingForecastVintage,
)


def build_series(
    year: int,
    values: list[str],
) -> PlanningSeries:
    return PlanningSeries(
        [
            PeriodValue(
                period=PlanningPeriod(year, month),
                value=Decimal(value),
            )
            for month, value in enumerate(values, start=1)
        ]
    )


def test_returns_latest_forecast_vintage() -> None:
    rf_jan = RollingForecastVintage(
        code="RF_JAN",
        as_of_period=PlanningPeriod(2027, 1),
        cadence=ForecastCadence.MONTHLY,
        values=build_series(2027, ["100", "150", "200"]),
    )

    rf_feb = RollingForecastVintage(
        code="RF_FEB",
        as_of_period=PlanningPeriod(2027, 2),
        cadence=ForecastCadence.MONTHLY,
        values=build_series(2027, ["100", "180", "220"]),
    )

    latest = RollingForecastEngine.latest_vintage([rf_jan, rf_feb])

    assert latest.code == "RF_FEB"


def test_latest_vintage_does_not_depend_on_input_order() -> None:
    rf_jan = RollingForecastVintage(
        code="RF_JAN",
        as_of_period=PlanningPeriod(2027, 1),
        cadence=ForecastCadence.MONTHLY,
        values=build_series(2027, ["100", "150"]),
    )

    rf_mar = RollingForecastVintage(
        code="RF_MAR",
        as_of_period=PlanningPeriod(2027, 3),
        cadence=ForecastCadence.MONTHLY,
        values=build_series(2027, ["100", "180", "220"]),
    )

    latest = RollingForecastEngine.latest_vintage([rf_mar, rf_jan])

    assert latest.code == "RF_MAR"


def test_monthly_forecast_advances_one_month() -> None:
    result = RollingForecastEngine.next_as_of_period(
        current_period=PlanningPeriod(2027, 2),
        cadence=ForecastCadence.MONTHLY,
    )

    assert result == PlanningPeriod(2027, 3)


def test_monthly_forecast_rolls_into_next_year() -> None:
    result = RollingForecastEngine.next_as_of_period(
        current_period=PlanningPeriod(2027, 12),
        cadence=ForecastCadence.MONTHLY,
    )

    assert result == PlanningPeriod(2028, 1)


def test_quarterly_forecast_advances_three_months() -> None:
    result = RollingForecastEngine.next_as_of_period(
        current_period=PlanningPeriod(2027, 3),
        cadence=ForecastCadence.QUARTERLY,
    )

    assert result == PlanningPeriod(2027, 6)


def test_quarterly_forecast_rolls_into_next_year() -> None:
    result = RollingForecastEngine.next_as_of_period(
        current_period=PlanningPeriod(2027, 11),
        cadence=ForecastCadence.QUARTERLY,
    )

    assert result == PlanningPeriod(2028, 2)


def test_compose_uses_actuals_for_closed_periods() -> None:
    actual = build_series(
        2027,
        ["110", "200"],
    )

    forecast = build_series(
        2027,
        ["100", "180", "230", "250"],
    )

    result = RollingForecastEngine.compose(
        actual=actual,
        forecast=forecast,
        closed_through=PlanningPeriod(2027, 2),
    )

    assert result.values.get(PlanningPeriod(2027, 1)) == Decimal("110")

    assert result.values.get(PlanningPeriod(2027, 2)) == Decimal("200")


def test_compose_uses_forecast_for_open_periods() -> None:
    actual = build_series(
        2027,
        ["110", "200"],
    )

    forecast = build_series(
        2027,
        ["100", "180", "230", "250"],
    )

    result = RollingForecastEngine.compose(
        actual=actual,
        forecast=forecast,
        closed_through=PlanningPeriod(2027, 2),
    )

    assert result.values.get(PlanningPeriod(2027, 3)) == Decimal("230")

    assert result.values.get(PlanningPeriod(2027, 4)) == Decimal("250")


def test_new_forecast_does_not_replace_closed_actuals() -> None:
    actual = build_series(
        2027,
        ["110", "200"],
    )

    revised_forecast = build_series(
        2027,
        ["999", "999", "260", "280"],
    )

    result = RollingForecastEngine.compose(
        actual=actual,
        forecast=revised_forecast,
        closed_through=PlanningPeriod(2027, 2),
    )

    assert result.values.get(PlanningPeriod(2027, 1)) == Decimal("110")

    assert result.values.get(PlanningPeriod(2027, 2)) == Decimal("200")

    assert result.values.get(PlanningPeriod(2027, 3)) == Decimal("260")


def test_rolling_forecast_total_combines_actual_and_forecast() -> None:
    actual = build_series(
        2027,
        ["110", "200"],
    )

    forecast = build_series(
        2027,
        ["100", "180", "230", "250"],
    )

    result = RollingForecastEngine.compose(
        actual=actual,
        forecast=forecast,
        closed_through=PlanningPeriod(2027, 2),
    )

    assert result.values.total() == Decimal("790")
