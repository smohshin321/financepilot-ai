from decimal import Decimal

import pytest
from app.modules.planning.engine import (
    ForecastCadence,
    ForecastHorizon,
    ForecastHorizonType,
    ForecastRollForwardEngine,
    MissingPlanningPeriodError,
    PeriodValue,
    PlanningPeriod,
    PlanningSeries,
    RollingForecastVintage,
)


def build_series(
    values: list[tuple[int, int, str]],
) -> PlanningSeries:
    return PlanningSeries(
        [
            PeriodValue(
                period=PlanningPeriod(year, month),
                value=Decimal(value),
            )
            for year, month, value in values
        ]
    )


def test_roll_forward_replaces_newly_closed_period_with_actual() -> None:
    prior = RollingForecastVintage(
        code="RF_FEB",
        as_of_period=PlanningPeriod(2027, 2),
        cadence=ForecastCadence.MONTHLY,
        values=build_series(
            [
                (2027, 1, "110"),
                (2027, 2, "200"),
                (2027, 3, "230"),
                (2027, 4, "250"),
                (2027, 5, "260"),
            ]
        ),
    )

    actual = build_series(
        [
            (2027, 1, "110"),
            (2027, 2, "200"),
            (2027, 3, "240"),
        ]
    )

    result = ForecastRollForwardEngine.roll_forward(
        code="RF_MAR",
        prior_vintage=prior,
        actual=actual,
        new_as_of_period=PlanningPeriod(2027, 3),
        horizon=ForecastHorizon(
            ForecastHorizonType.ROLLING,
            months=2,
        ),
    )

    assert result.values.get(PlanningPeriod(2027, 3)) == Decimal("240")

    assert result.values.get(PlanningPeriod(2027, 4)) == Decimal("250")

    assert result.values.get(PlanningPeriod(2027, 5)) == Decimal("260")


def test_roll_forward_applies_revised_future_value() -> None:
    prior = RollingForecastVintage(
        code="RF_FEB",
        as_of_period=PlanningPeriod(2027, 2),
        cadence=ForecastCadence.MONTHLY,
        values=build_series(
            [
                (2027, 1, "110"),
                (2027, 2, "200"),
                (2027, 3, "230"),
                (2027, 4, "250"),
                (2027, 5, "260"),
            ]
        ),
    )

    actual = build_series(
        [
            (2027, 1, "110"),
            (2027, 2, "200"),
            (2027, 3, "240"),
        ]
    )

    revised = build_series(
        [
            (2027, 5, "280"),
        ]
    )

    result = ForecastRollForwardEngine.roll_forward(
        code="RF_MAR",
        prior_vintage=prior,
        actual=actual,
        new_as_of_period=PlanningPeriod(2027, 3),
        horizon=ForecastHorizon(
            ForecastHorizonType.ROLLING,
            months=2,
        ),
        revised_values=revised,
    )

    assert result.values.get(PlanningPeriod(2027, 4)) == Decimal("250")

    assert result.values.get(PlanningPeriod(2027, 5)) == Decimal("280")


def test_rolling_horizon_can_extend_with_new_assumption() -> None:
    prior = RollingForecastVintage(
        code="RF_MAR",
        as_of_period=PlanningPeriod(2027, 3),
        cadence=ForecastCadence.MONTHLY,
        values=build_series(
            [
                (2027, 1, "110"),
                (2027, 2, "200"),
                (2027, 3, "240"),
                (2027, 4, "250"),
                (2027, 5, "280"),
            ]
        ),
    )

    actual = build_series(
        [
            (2027, 1, "110"),
            (2027, 2, "200"),
            (2027, 3, "240"),
            (2027, 4, "255"),
        ]
    )

    revised = build_series(
        [
            (2027, 6, "300"),
        ]
    )

    result = ForecastRollForwardEngine.roll_forward(
        code="RF_APR",
        prior_vintage=prior,
        actual=actual,
        new_as_of_period=PlanningPeriod(2027, 4),
        horizon=ForecastHorizon(
            ForecastHorizonType.ROLLING,
            months=2,
        ),
        revised_values=revised,
    )

    assert result.values.get(PlanningPeriod(2027, 4)) == Decimal("255")

    assert result.values.get(PlanningPeriod(2027, 5)) == Decimal("280")

    assert result.values.get(PlanningPeriod(2027, 6)) == Decimal("300")


def test_roll_forward_rejects_missing_new_horizon_value() -> None:
    prior = RollingForecastVintage(
        code="RF_MAR",
        as_of_period=PlanningPeriod(2027, 3),
        cadence=ForecastCadence.MONTHLY,
        values=build_series(
            [
                (2027, 1, "110"),
                (2027, 2, "200"),
                (2027, 3, "240"),
                (2027, 4, "250"),
                (2027, 5, "280"),
            ]
        ),
    )

    actual = build_series(
        [
            (2027, 1, "110"),
            (2027, 2, "200"),
            (2027, 3, "240"),
            (2027, 4, "255"),
        ]
    )

    with pytest.raises(MissingPlanningPeriodError):
        ForecastRollForwardEngine.roll_forward(
            code="RF_APR",
            prior_vintage=prior,
            actual=actual,
            new_as_of_period=PlanningPeriod(2027, 4),
            horizon=ForecastHorizon(
                ForecastHorizonType.ROLLING,
                months=2,
            ),
        )


def test_roll_forward_does_not_modify_prior_vintage() -> None:
    prior = RollingForecastVintage(
        code="RF_FEB",
        as_of_period=PlanningPeriod(2027, 2),
        cadence=ForecastCadence.MONTHLY,
        values=build_series(
            [
                (2027, 1, "110"),
                (2027, 2, "200"),
                (2027, 3, "230"),
                (2027, 4, "250"),
            ]
        ),
    )

    original_march = prior.values.get(PlanningPeriod(2027, 3))

    actual = build_series(
        [
            (2027, 1, "110"),
            (2027, 2, "200"),
            (2027, 3, "240"),
        ]
    )

    revised = build_series(
        [
            (2027, 4, "270"),
        ]
    )

    ForecastRollForwardEngine.roll_forward(
        code="RF_MAR",
        prior_vintage=prior,
        actual=actual,
        new_as_of_period=PlanningPeriod(2027, 3),
        horizon=ForecastHorizon(
            ForecastHorizonType.ROLLING,
            months=1,
        ),
        revised_values=revised,
    )

    assert prior.code == "RF_FEB"
    assert prior.values.get(PlanningPeriod(2027, 3)) == original_march
    assert original_march == Decimal("230")
