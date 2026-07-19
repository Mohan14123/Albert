"""Auth endpoint tests — register, login, token rotation, session management."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    """New user registration returns 201 with user_id."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@albert.dev",
            "password": "Secure@Pass123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "user_id" in data["data"]


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient, test_user: dict):
    """Registering with an existing email returns 400."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@albert.dev",
            "password": "TestPassword@123",
            "full_name": "Duplicate",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_weak_password(async_client: AsyncClient):
    """Registering with a weak password returns 400."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "weak@albert.dev", "password": "short", "full_name": "Weak"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, test_user: dict):
    """Valid credentials return access and refresh tokens."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@albert.dev", "password": "TestPassword@123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient, test_user: dict):
    """Wrong password returns 401."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@albert.dev", "password": "WrongPassword@123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(async_client: AsyncClient):
    """Login with unknown email returns 401."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@albert.dev", "password": "TestPassword@123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(async_client: AsyncClient, auth_headers: dict):
    """Authenticated /auth/me returns the current user."""
    response = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@albert.dev"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_current_user_no_token(async_client: AsyncClient):
    """/auth/me without token returns 401."""
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_tokens(async_client: AsyncClient, test_user: dict):
    """Refresh token rotation returns new access + refresh tokens."""
    # First login to get tokens
    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@albert.dev", "password": "TestPassword@123"},
    )
    refresh_token = login.json()["refresh_token"]

    # Refresh
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["refresh_token"] != refresh_token  # token was rotated


@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient, test_user: dict, auth_headers: dict):
    """Logout revokes the refresh token."""
    # Login again to get a fresh refresh token
    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@albert.dev", "password": "TestPassword@123"},
    )
    refresh_token = login.json()["refresh_token"]

    response = await async_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Refreshing with the revoked token should fail
    retry = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert retry.status_code == 401


@pytest.mark.asyncio
async def test_logout_all(async_client: AsyncClient, auth_headers: dict):
    """Logout-all revokes all sessions."""
    response = await async_client.post(
        "/api/v1/auth/logout-all",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
