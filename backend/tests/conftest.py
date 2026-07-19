"""Pytest configuration, fixtures, and async test database setup."""

from collections.abc import AsyncGenerator

import pytest_asyncio
from app.api.v1 import auth as auth_router
from app.api.v1 import chats as chats_router
from app.api.v1 import integrations as integrations_router
from app.api.v1 import messages as messages_router
from app.api.v1 import users as users_router
from app.core.dependencies import get_db
from app.database.base import Base
from app.database.models import (  # noqa: F401 — ensure all models are registered
    Chat,
    Integration,
    Message,
    OAuthToken,
    RefreshToken,
    User,
    UserSettings,
)
from app.main import app
from app.services import NullEventDispatcher
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ── In-memory async SQLite for tests ──────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_db():
    """Create all tables once for the test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a fresh transactional DB session per test, rolled back after."""
    async with TestSessionLocal() as session, session.begin():
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an httpx AsyncClient with the test DB and NullEventDispatcher injected.
    """

    async def _override_get_db():
        yield db_session

    _null = NullEventDispatcher()

    def _override_auth_service(db: AsyncSession = Depends(_override_get_db)):
        from app.repositories.refresh_token_repository import RefreshTokenRepository
        from app.repositories.session_repository import SessionRepository
        from app.repositories.user_repository import UserRepository
        from app.repositories.user_settings_repository import UserSettingsRepository
        from app.services.auth_service import AuthService

        return AuthService(
            users=UserRepository(db_session),
            refresh_tokens=RefreshTokenRepository(db_session),
            user_settings=UserSettingsRepository(db_session),
            sessions=SessionRepository(db_session),
            events=_null,
        )

    def _override_user_service(db: AsyncSession = Depends(_override_get_db)):
        from app.repositories.user_repository import UserRepository
        from app.repositories.user_settings_repository import UserSettingsRepository
        from app.services.user_service import UserService

        return UserService(
            users=UserRepository(db_session),
            settings=UserSettingsRepository(db_session),
            events=_null,
        )

    def _override_chat_service(db: AsyncSession = Depends(_override_get_db)):
        from app.repositories.chat_repository import ChatRepository
        from app.services.chat_service import ChatService

        return ChatService(chats=ChatRepository(db_session), events=_null)

    def _override_message_service(db: AsyncSession = Depends(_override_get_db)):
        from app.repositories.chat_repository import ChatRepository
        from app.repositories.message_repository import MessageRepository
        from app.services.message_service import MessageService

        return MessageService(
            chats=ChatRepository(db_session),
            messages=MessageRepository(db_session),
            events=_null,
        )

    def _override_integration_service(db: AsyncSession = Depends(_override_get_db)):
        from app.repositories.integration_repository import IntegrationRepository
        from app.repositories.oauth_token_repository import OAuthTokenRepository
        from app.services.integration_service import IntegrationService

        return IntegrationService(
            integrations=IntegrationRepository(db_session),
            tokens=OAuthTokenRepository(db_session),
            events=_null,
        )

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[auth_router._get_auth_service] = _override_auth_service
    app.dependency_overrides[users_router._get_user_service] = _override_user_service
    app.dependency_overrides[chats_router._get_chat_service] = _override_chat_service
    app.dependency_overrides[messages_router._get_message_service] = (
        _override_message_service
    )
    app.dependency_overrides[integrations_router._get_integration_service] = (
        _override_integration_service
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(async_client: AsyncClient) -> dict:
    """Register and return a test user."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@albert.dev",
            "password": "TestPassword@123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient, test_user: dict) -> dict:
    """Login as the test user and return Authorization headers."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@albert.dev", "password": "TestPassword@123"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
