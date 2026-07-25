import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
