from app.modules.planning.engine.period import PlanningPeriod


class PlanningEngineError(Exception):
    """Base exception for planning-engine failures."""


class MissingDriverError(PlanningEngineError):
    """Raised when a required planning driver is unavailable."""

    def __init__(self, driver_code: str) -> None:
        super().__init__(f"Required planning driver '{driver_code}' is missing.")
        self.driver_code = driver_code


class InvalidDriverValueError(PlanningEngineError):
    """Raised when a driver contains an invalid financial value."""


class MissingPlanningPeriodError(PlanningEngineError):
    """Raised when a required planning period is unavailable."""

    def __init__(self, period: PlanningPeriod) -> None:
        super().__init__(f"Planning period '{period.code}' is missing.")
        self.period = period


class DuplicatePlanningPeriodError(PlanningEngineError):
    """Raised when a planning series contains a duplicate period."""

    def __init__(self, period: PlanningPeriod) -> None:
        super().__init__(f"Planning period '{period.code}' is duplicated.")
        self.period = period


class PeriodAlignmentError(PlanningEngineError):
    """Raised when planning series use different period calendars."""

    def __init__(
        self,
        *,
        left_only: set[PlanningPeriod],
        right_only: set[PlanningPeriod],
    ) -> None:
        self.left_only = left_only
        self.right_only = right_only

        missing_from_right = ", ".join(period.code for period in sorted(left_only))
        missing_from_left = ", ".join(period.code for period in sorted(right_only))

        details: list[str] = []

        if missing_from_right:
            details.append(f"missing from right: {missing_from_right}")

        if missing_from_left:
            details.append(f"missing from left: {missing_from_left}")

        message = "; ".join(details)

        super().__init__(f"Planning series periods do not align ({message}).")
