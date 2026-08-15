import pytest
from app.modules.planning.engine import (
    ForecastHorizon,
    ForecastHorizonEngine,
    ForecastHorizonType,
    PlanningPeriod,
)


def test_fiscal_year_horizon_runs_to_year_end() -> None:
    periods = ForecastHorizonEngine.periods(
        as_of_period=PlanningPeriod(2027, 2),
        horizon=ForecastHorizon(ForecastHorizonType.FISCAL_YEAR),
    )

    assert periods[0] == PlanningPeriod(2027, 3)
    assert periods[-1] == PlanningPeriod(2027, 12)
    assert len(periods) == 10


def test_fiscal_year_horizon_after_year_end_starts_next_year() -> None:
    periods = ForecastHorizonEngine.periods(
        as_of_period=PlanningPeriod(2027, 12),
        horizon=ForecastHorizon(ForecastHorizonType.FISCAL_YEAR),
    )

    assert periods[0] == PlanningPeriod(2028, 1)
    assert periods[-1] == PlanningPeriod(2028, 12)
    assert len(periods) == 12


def test_non_calendar_fiscal_year_horizon() -> None:
    periods = ForecastHorizonEngine.periods(
        as_of_period=PlanningPeriod(2027, 9),
        horizon=ForecastHorizon(ForecastHorizonType.FISCAL_YEAR),
        fiscal_year_end_month=6,
    )

    assert periods[0] == PlanningPeriod(2027, 10)
    assert periods[-1] == PlanningPeriod(2028, 6)
    assert len(periods) == 9


def test_rolling_twelve_month_horizon() -> None:
    periods = ForecastHorizonEngine.periods(
        as_of_period=PlanningPeriod(2027, 2),
        horizon=ForecastHorizon(
            ForecastHorizonType.ROLLING,
            months=12,
        ),
    )

    assert periods[0] == PlanningPeriod(2027, 3)
    assert periods[-1] == PlanningPeriod(2028, 2)
    assert len(periods) == 12


def test_rolling_eighteen_month_horizon() -> None:
    periods = ForecastHorizonEngine.periods(
        as_of_period=PlanningPeriod(2027, 10),
        horizon=ForecastHorizon(
            ForecastHorizonType.ROLLING,
            months=18,
        ),
    )

    assert periods[0] == PlanningPeriod(2027, 11)
    assert periods[-1] == PlanningPeriod(2029, 4)
    assert len(periods) == 18


@pytest.mark.parametrize(
    "months",
    [None, 0, -1],
)
def test_rolling_horizon_rejects_invalid_months(
    months: int | None,
) -> None:
    with pytest.raises(ValueError):
        ForecastHorizon(
            horizon_type=ForecastHorizonType.ROLLING,
            months=months,
        )


def test_fiscal_year_horizon_rejects_month_configuration() -> None:
    with pytest.raises(ValueError):
        ForecastHorizon(
            horizon_type=ForecastHorizonType.FISCAL_YEAR,
            months=12,
        )


@pytest.mark.parametrize(
    "fiscal_year_end_month",
    [0, 13],
)
def test_rejects_invalid_fiscal_year_end_month(
    fiscal_year_end_month: int,
) -> None:
    with pytest.raises(ValueError):
        ForecastHorizonEngine.periods(
            as_of_period=PlanningPeriod(2027, 2),
            horizon=ForecastHorizon(ForecastHorizonType.FISCAL_YEAR),
            fiscal_year_end_month=fiscal_year_end_month,
        )
