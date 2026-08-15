from decimal import Decimal

import pytest
from app.modules.planning.engine import (
    ForecastCadence,
    ForecastGovernanceEngine,
    ForecastGovernanceError,
    PeriodValue,
    PlanningPeriod,
    PlanningSeries,
    RollingForecastVintage,
)


def build_vintage(
    *,
    code: str,
    year: int,
    month: int,
    cadence: ForecastCadence,
) -> RollingForecastVintage:
    period = PlanningPeriod(year, month)

    return RollingForecastVintage(
        code=code,
        as_of_period=period,
        cadence=cadence,
        values=PlanningSeries(
            [
                PeriodValue(
                    period=period,
                    value=Decimal("100"),
                )
            ]
        ),
    )


def test_monthly_vintage_accepts_next_month() -> None:
    prior = build_vintage(
        code="RF_FEB",
        year=2027,
        month=2,
        cadence=ForecastCadence.MONTHLY,
    )

    ForecastGovernanceEngine.validate_next_vintage(
        prior_vintage=prior,
        new_as_of_period=PlanningPeriod(2027, 3),
    )


def test_monthly_vintage_rejects_skipped_month() -> None:
    prior = build_vintage(
        code="RF_FEB",
        year=2027,
        month=2,
        cadence=ForecastCadence.MONTHLY,
    )

    with pytest.raises(ForecastGovernanceError):
        ForecastGovernanceEngine.validate_next_vintage(
            prior_vintage=prior,
            new_as_of_period=PlanningPeriod(2027, 4),
        )


def test_quarterly_vintage_accepts_three_month_advance() -> None:
    prior = build_vintage(
        code="RF_MAR",
        year=2027,
        month=3,
        cadence=ForecastCadence.QUARTERLY,
    )

    ForecastGovernanceEngine.validate_next_vintage(
        prior_vintage=prior,
        new_as_of_period=PlanningPeriod(2027, 6),
    )


def test_quarterly_vintage_rejects_wrong_period() -> None:
    prior = build_vintage(
        code="RF_MAR",
        year=2027,
        month=3,
        cadence=ForecastCadence.QUARTERLY,
    )

    with pytest.raises(ForecastGovernanceError):
        ForecastGovernanceEngine.validate_next_vintage(
            prior_vintage=prior,
            new_as_of_period=PlanningPeriod(2027, 5),
        )


def test_monthly_cadence_rolls_across_year_end() -> None:
    prior = build_vintage(
        code="RF_DEC",
        year=2027,
        month=12,
        cadence=ForecastCadence.MONTHLY,
    )

    assert ForecastGovernanceEngine.expected_next_period(
        prior_vintage=prior,
    ) == PlanningPeriod(2028, 1)


def test_quarterly_cadence_rolls_across_year_end() -> None:
    prior = build_vintage(
        code="RF_NOV",
        year=2027,
        month=11,
        cadence=ForecastCadence.QUARTERLY,
    )

    assert ForecastGovernanceEngine.expected_next_period(
        prior_vintage=prior,
    ) == PlanningPeriod(2028, 2)


def test_duplicate_as_of_period_is_rejected() -> None:
    first = build_vintage(
        code="RF_FEB_A",
        year=2027,
        month=2,
        cadence=ForecastCadence.MONTHLY,
    )

    second = build_vintage(
        code="RF_FEB_B",
        year=2027,
        month=2,
        cadence=ForecastCadence.MONTHLY,
    )

    with pytest.raises(ForecastGovernanceError):
        ForecastGovernanceEngine.validate_unique_as_of_periods([first, second])


def test_unique_as_of_periods_are_accepted() -> None:
    first = build_vintage(
        code="RF_FEB",
        year=2027,
        month=2,
        cadence=ForecastCadence.MONTHLY,
    )

    second = build_vintage(
        code="RF_MAR",
        year=2027,
        month=3,
        cadence=ForecastCadence.MONTHLY,
    )

    ForecastGovernanceEngine.validate_unique_as_of_periods([first, second])


def test_mixed_cadences_are_rejected() -> None:
    monthly = build_vintage(
        code="RF_FEB",
        year=2027,
        month=2,
        cadence=ForecastCadence.MONTHLY,
    )

    quarterly = build_vintage(
        code="RF_MAY",
        year=2027,
        month=5,
        cadence=ForecastCadence.QUARTERLY,
    )

    with pytest.raises(ForecastGovernanceError):
        ForecastGovernanceEngine.validate_consistent_cadence([monthly, quarterly])


def test_consistent_cadence_is_accepted() -> None:
    first = build_vintage(
        code="RF_FEB",
        year=2027,
        month=2,
        cadence=ForecastCadence.MONTHLY,
    )

    second = build_vintage(
        code="RF_MAR",
        year=2027,
        month=3,
        cadence=ForecastCadence.MONTHLY,
    )

    ForecastGovernanceEngine.validate_consistent_cadence([first, second])
