from unittest.mock import AsyncMock, MagicMock

import pytest
from app.core.database.health import database_is_ready
from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.mark.asyncio
async def test_database_is_ready_returns_true_for_successful_query() -> None:
    engine = MagicMock(spec=AsyncEngine)
    connection = AsyncMock()
    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = connection
    engine.connect.return_value = context_manager

    assert await database_is_ready(engine) is True
    connection.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_database_is_ready_returns_false_for_connection_error() -> None:
    engine = MagicMock(spec=AsyncEngine)
    context_manager = AsyncMock()
    context_manager.__aenter__.side_effect = RuntimeError("database unavailable")
    engine.connect.return_value = context_manager

    assert await database_is_ready(engine) is False
