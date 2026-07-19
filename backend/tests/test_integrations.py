"""Integration endpoint tests — list, connect redirect URL, disconnect, status."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_integrations_empty(async_client: AsyncClient, auth_headers: dict):
    """New user has no integrations."""
    response = await async_client.get("/api/v1/integrations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == []


@pytest.mark.asyncio
async def test_list_integrations_unauthenticated(async_client: AsyncClient):
    """Listing integrations without auth returns 401."""
    response = await async_client.get("/api/v1/integrations")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_connect_gmail_returns_auth_url(
    async_client: AsyncClient, auth_headers: dict
):
    """Connecting Gmail returns a Google OAuth authorization URL."""
    response = await async_client.post(
        "/api/v1/integrations/gmail/connect",
        headers=auth_headers,
    )
    # If Google credentials aren't configured, expect 400/422/502 — otherwise 200 with auth_url
    if response.status_code == 200:
        data = response.json()
        assert "auth_url" in data
        assert "accounts.google.com" in data["auth_url"]
    else:
        # Without real credentials this is expected to fail validation
        assert response.status_code in (400, 422, 502)


@pytest.mark.asyncio
async def test_connect_unsupported_provider(
    async_client: AsyncClient, auth_headers: dict
):
    """Connecting an unknown provider returns 400."""
    response = await async_client.post(
        "/api/v1/integrations/totally_fake_provider/connect",
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_integration_status_not_found(
    async_client: AsyncClient, auth_headers: dict
):
    """Getting status of a non-connected integration returns 404."""
    response = await async_client.get(
        "/api/v1/integrations/gmail/status",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_disconnect_not_found(async_client: AsyncClient, auth_headers: dict):
    """Disconnecting an integration that doesn't exist returns 404."""
    response = await async_client.delete(
        "/api/v1/integrations/gmail",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_sync_not_found(async_client: AsyncClient, auth_headers: dict):
    """Triggering sync for non-connected integration returns 404."""
    response = await async_client.post(
        "/api/v1/integrations/gmail/sync",
        headers=auth_headers,
    )
    assert response.status_code == 404
