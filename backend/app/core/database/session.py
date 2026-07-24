from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings


def create_engine(settings: Settings | None = None) -> AsyncEngine:
    """Create the application SQLAlchemy engine."""
    resolved = settings or get_settings()
    return create_async_engine(
        resolved.database_url,
        echo=resolved.database_echo,
        pool_pre_ping=True,
        pool_size=resolved.database_pool_size,
        max_overflow=resolved.database_max_overflow,
        pool_timeout=resolved.database_pool_timeout_seconds,
        connect_args={"connect_timeout": resolved.database_command_timeout_seconds},
    )


@lru_cache
def get_engine() -> AsyncEngine:
    """Return the process-wide SQLAlchemy engine."""
    return create_engine()


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the process-wide asynchronous session factory."""
    return async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Provide a transaction-scoped database session to API dependencies."""
    async with get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
