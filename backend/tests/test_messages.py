"""Message endpoint tests — send, list, SSE stream."""

import pytest
from httpx import AsyncClient


async def _create_chat(client: AsyncClient, headers: dict) -> str:
    r = await client.post(
        "/api/v1/chats", json={"title": "Msg Test Chat"}, headers=headers
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


@pytest.mark.asyncio
async def test_send_message(async_client: AsyncClient, auth_headers: dict):
    """Sending a message returns 201 with message_id and status=pending."""
    chat_id = await _create_chat(async_client, auth_headers)
    response = await async_client.post(
        f"/api/v1/chats/{chat_id}/messages",
        json={"content": "Hello Albert!"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "message_id" in data["data"]
    assert data["data"]["status"] == "pending"


@pytest.mark.asyncio
async def test_send_message_unauthenticated(
    async_client: AsyncClient, auth_headers: dict
):
    """Sending a message without auth returns 401."""
    chat_id = await _create_chat(async_client, auth_headers)
    response = await async_client.post(
        f"/api/v1/chats/{chat_id}/messages",
        json={"content": "Hello"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_messages_empty(async_client: AsyncClient, auth_headers: dict):
    """Listing messages on a new chat returns empty list."""
    chat_id = await _create_chat(async_client, auth_headers)
    response = await async_client.get(
        f"/api/v1/chats/{chat_id}/messages",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_messages_with_data(async_client: AsyncClient, auth_headers: dict):
    """After sending messages, list returns them ordered."""
    chat_id = await _create_chat(async_client, auth_headers)

    for content in ["First message", "Second message", "Third message"]:
        await async_client.post(
            f"/api/v1/chats/{chat_id}/messages",
            json={"content": content},
            headers=auth_headers,
        )

    response = await async_client.get(
        f"/api/v1/chats/{chat_id}/messages?page=1&limit=10",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["items"][0]["role"] == "user"


@pytest.mark.asyncio
async def test_send_message_to_other_users_chat(
    async_client: AsyncClient, auth_headers: dict
):
    """Sending a message to another user's chat returns 403 or 404."""
    # Create chat as primary user
    chat_id = await _create_chat(async_client, auth_headers)

    # Register and login as another user
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "intruder@albert.dev",
            "password": "Intrude@Pass1",
            "full_name": "Intruder",
        },
    )
    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "intruder@albert.dev", "password": "Intrude@Pass1"},
    )
    intruder_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = await async_client.post(
        f"/api/v1/chats/{chat_id}/messages",
        json={"content": "I shouldn't be here"},
        headers=intruder_headers,
    )
    assert response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_sse_stream_returns_event_stream(
    async_client: AsyncClient, auth_headers: dict
):
    """SSE stream endpoint returns text/event-stream content type."""
    chat_id = await _create_chat(async_client, auth_headers)
    # Use a short timeout — we just check content-type, not the stream body
    response = await async_client.get(
        f"/api/v1/chats/{chat_id}/messages/stream",
        headers=auth_headers,
        timeout=5.0,
    )
    # Accept 200 (with stream) or the test may time out - check header
    assert response.headers.get("content-type", "").startswith("text/event-stream")
