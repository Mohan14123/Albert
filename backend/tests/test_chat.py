"""Chat endpoint tests — full CRUD lifecycle and ownership enforcement."""

import pytest
from httpx import AsyncClient


async def _create_chat(async_client: AsyncClient, auth_headers: dict, title: str = "Test Chat") -> dict:
    """Helper to create a chat and return its JSON response."""
    response = await async_client.post(
        "/api/v1/chats",
        json={"title": title},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_create_chat(async_client: AsyncClient, auth_headers: dict):
    """Creating a chat returns 201 with correct data."""
    response = await async_client.post(
        "/api/v1/chats",
        json={"title": "My First Chat"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Chat"
    assert data["archived"] is False
    assert "id" in data


@pytest.mark.asyncio
async def test_create_chat_unauthenticated(async_client: AsyncClient):
    """Creating a chat without auth returns 401."""
    response = await async_client.post("/api/v1/chats", json={"title": "No Auth"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_chats_empty(async_client: AsyncClient, auth_headers: dict):
    """Listing chats for a fresh user returns empty list."""
    response = await async_client.get("/api/v1/chats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert "total" in data


@pytest.mark.asyncio
async def test_list_chats_with_data(async_client: AsyncClient, auth_headers: dict):
    """After creating chats, list returns them paginated."""
    for i in range(3):
        await _create_chat(async_client, auth_headers, f"Chat {i}")

    response = await async_client.get("/api/v1/chats?page=1&limit=10", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 3


@pytest.mark.asyncio
async def test_get_chat(async_client: AsyncClient, auth_headers: dict):
    """Getting an existing chat by ID returns correct data."""
    created = await _create_chat(async_client, auth_headers)
    chat_id = created["id"]

    response = await async_client.get(f"/api/v1/chats/{chat_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == chat_id


@pytest.mark.asyncio
async def test_get_nonexistent_chat(async_client: AsyncClient, auth_headers: dict):
    """Getting a chat that doesn't exist returns 404."""
    import uuid
    response = await async_client.get(
        f"/api/v1/chats/{uuid.uuid4()}", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rename_chat(async_client: AsyncClient, auth_headers: dict):
    """Renaming a chat updates its title."""
    created = await _create_chat(async_client, auth_headers)
    chat_id = created["id"]

    response = await async_client.patch(
        f"/api/v1/chats/{chat_id}",
        json={"title": "Renamed Chat"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Renamed Chat"


@pytest.mark.asyncio
async def test_delete_chat(async_client: AsyncClient, auth_headers: dict):
    """Deleting a chat returns 204; subsequent get returns 404."""
    created = await _create_chat(async_client, auth_headers)
    chat_id = created["id"]

    delete_response = await async_client.delete(
        f"/api/v1/chats/{chat_id}", headers=auth_headers
    )
    assert delete_response.status_code == 204

    get_response = await async_client.get(
        f"/api/v1/chats/{chat_id}", headers=auth_headers
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_chat_ownership_enforcement(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session,
):
    """User A cannot access User B's chat."""
    # Create chat as User A
    created = await _create_chat(async_client, auth_headers)
    chat_id = created["id"]

    # Register and login as User B
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "userb@albert.dev",
            "password": "AnotherPass@456",
            "full_name": "User B",
        },
    )
    login_b = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "userb@albert.dev", "password": "AnotherPass@456"},
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B tries to access User A's chat
    response = await async_client.get(f"/api/v1/chats/{chat_id}", headers=headers_b)
    assert response.status_code in (403, 404)
