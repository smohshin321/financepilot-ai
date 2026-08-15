from app.modules.planning.engine.exceptions import MissingPlanningPeriodError
from app.modules.planning.engine.forecast_horizon import (
    ForecastHorizon,
    ForecastHorizonEngine,
)
from app.modules.planning.engine.period import PlanningPeriod
from app.modules.planning.engine.rolling_forecast import RollingForecastVintage
from app.modules.planning.engine.series import (
    PeriodValue,
    PlanningSeries,
)


class ForecastRollForwardEngine:
    """Create a new rolling-forecast vintage from a prior vintage."""

    @staticmethod
    def roll_forward(
        *,
        code: str,
        prior_vintage: RollingForecastVintage,
        actual: PlanningSeries,
        new_as_of_period: PlanningPeriod,
        horizon: ForecastHorizon,
        revised_values: PlanningSeries | None = None,
        fiscal_year_end_month: int = 12,
    ) -> RollingForecastVintage:
        """Roll a forecast forward while preserving closed actuals."""

        if new_as_of_period <= prior_vintage.as_of_period:
            raise ValueError("New forecast as-of period must be later than the prior vintage.")

        forecast_periods = ForecastHorizonEngine.periods(
            as_of_period=new_as_of_period,
            horizon=horizon,
            fiscal_year_end_month=fiscal_year_end_month,
        )

        prior_periods = set(prior_vintage.values.periods())

        revised_periods = set(revised_values.periods()) if revised_values is not None else set()

        values = [
            PeriodValue(
                period=period,
                value=actual.get(period),
            )
            for period in actual.periods()
            if period <= new_as_of_period
        ]

        for period in forecast_periods:
            if period in revised_periods:
                assert revised_values is not None
                value = revised_values.get(period)
            elif period in prior_periods:
                value = prior_vintage.values.get(period)
            else:
                raise MissingPlanningPeriodError(period)

            values.append(
                PeriodValue(
                    period=period,
                    value=value,
                )
            )

        return RollingForecastVintage(
            code=code,
            as_of_period=new_as_of_period,
            cadence=prior_vintage.cadence,
            values=PlanningSeries(values),
        )
