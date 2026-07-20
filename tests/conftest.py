import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

# Import the backend app
from app.main import app  # type: ignore
from app.database.base import Base  # type: ignore
from app.database.session import engine  # type: ignore


@pytest.fixture(scope="session")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_client(setup_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_user_token():
    return "mock_jwt_token_for_testing"


@pytest.fixture
def test_user_id():
    return uuid4()
