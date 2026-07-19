"""Health endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(async_client: AsyncClient):
    """/health always returns 200 with status=healthy."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_version_returns_version_string(async_client: AsyncClient):
    """/version returns a non-empty version string."""
    response = await async_client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert len(data["version"]) > 0
    assert "environment" in data


@pytest.mark.asyncio
async def test_ready_returns_status(async_client: AsyncClient):
    """
    /ready returns 200 (all checks OK) or 503 (some degraded).
    In test environment, infra may not be running — we just verify the shape.
    """
    response = await async_client.get("/api/v1/ready")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "postgres" in data["checks"]
    assert "redis" in data["checks"]
    assert "rabbitmq" in data["checks"]
