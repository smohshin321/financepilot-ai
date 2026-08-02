from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from app.core.database import get_db_session
from app.core.security import create_access_token
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


async def override_db_session() -> AsyncIterator[AsyncSession]:
    yield AsyncMock(spec=AsyncSession)


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_db_session] = override_db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def build_access_token() -> str:
    return create_access_token(
        user_id=uuid4(),
        organization_id=uuid4(),
        membership_id=uuid4(),
        role_ids=[uuid4()],
    )


def test_protected_endpoint_requires_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/protected")

    assert response.status_code == 401


def test_protected_endpoint_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_protected_endpoint_rejects_missing_permission(
    client: TestClient,
) -> None:
    token = build_access_token()

    with patch(
        "app.modules.identity.api.authorization.AuthorizationService.has_permission",
        new=AsyncMock(return_value=False),
    ):
        response = client.get(
            "/api/v1/auth/protected",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Permission 'budget.read' is required."


def test_protected_endpoint_allows_required_permission(
    client: TestClient,
) -> None:
    token = build_access_token()

    with patch(
        "app.modules.identity.api.authorization.AuthorizationService.has_permission",
        new=AsyncMock(return_value=True),
    ):
        response = client.get(
            "/api/v1/auth/protected",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json() == {"message": "Access granted"}
