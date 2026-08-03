class PlanningCycleNotFoundError(Exception):
    """Raised when a planning cycle cannot be found."""


class InvalidPlanningCycleDateRangeError(Exception):
    """Raised when a planning cycle end date precedes its start date."""


class InvalidFiscalYearError(Exception):
    """Raised when a fiscal year falls outside the supported range."""


class BudgetVersionNotFoundError(Exception):
    """Raised when a budget version cannot be found."""


class BudgetVersionLockedError(Exception):
    """Raised when attempting to modify a locked budget version."""


class ActiveBudgetVersionExistsError(Exception):
    """Raised when another active version already exists."""


class BudgetLineNotFoundError(Exception):
    """Raised when a budget line cannot be found."""


class InvalidBudgetAmountError(Exception):
    """Raised when a budget amount is invalid."""
