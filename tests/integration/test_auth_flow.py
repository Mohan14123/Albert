import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_protected_route_without_token(async_client: AsyncClient):
    response = await async_client.get("/api/v1/chats")
    # Should be 401 Unauthorized because no token is provided
    assert response.status_code == 401
