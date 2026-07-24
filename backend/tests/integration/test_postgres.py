import pytest
from sqlalchemy import text

from app.core.database import get_engine


@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgres_executes_query() -> None:
    async with get_engine().connect() as connection:
        result = await connection.scalar(text("SELECT 1"))
    assert result == 1
