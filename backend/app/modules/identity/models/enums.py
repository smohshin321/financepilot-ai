from enum import StrEnum


class OrganizationStatus(StrEnum):
    """Lifecycle states supported by an organization tenant."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
