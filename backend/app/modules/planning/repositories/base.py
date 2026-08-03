from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Base class for Planning module repositories."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
