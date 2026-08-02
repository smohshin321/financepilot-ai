class InvalidCredentialsError(Exception):
    """Raised when supplied authentication credentials are invalid."""


class InactiveUserError(Exception):
    """Raised when an inactive user attempts to authenticate."""


class MembershipNotFoundError(Exception):
    """Raised when a user has no active organization membership."""
