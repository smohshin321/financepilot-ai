from dataclasses import dataclass


@dataclass(frozen=True, slots=True, order=True)
class PlanningPeriod:
    """Represents a fiscal planning period."""

    year: int
    month: int

    def __post_init__(self) -> None:
        if not 1 <= self.month <= 12:
            raise ValueError("Month must be between 1 and 12.")

        if not 2000 <= self.year <= 2200:
            raise ValueError("Year must be between 2000 and 2200.")

    @property
    def code(self) -> str:
        """Return a stable period code."""

        return f"{self.year}-{self.month:02d}"
