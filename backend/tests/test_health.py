from unittest.mock import AsyncMock, patch

from app.core.config import get_settings
from fastapi.testclient import TestClient


def test_health_endpoint_returns_service_status(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    settings = get_settings()

    assert response.json() == {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }


def test_versioned_health_endpoint_is_available(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_readiness_returns_ready_when_database_is_available(client: TestClient) -> None:
    with (
        patch("app.api.routes.health.get_engine"),
        patch("app.api.routes.health.database_is_ready", new=AsyncMock(return_value=True)),
    ):
        response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "available"}


def test_readiness_returns_503_when_database_is_unavailable(client: TestClient) -> None:
    with (
        patch("app.api.routes.health.get_engine"),
        patch("app.api.routes.health.database_is_ready", new=AsyncMock(return_value=False)),
    ):
        response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "not_ready", "database": "unavailable"}
