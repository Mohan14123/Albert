from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.settings import settings

engine_kwargs: dict[str, Any] = {
    "echo": settings.debug,
}

if not str(settings.database_url).startswith("sqlite"):
    engine_kwargs.update(
        {
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
        }
    )

# Create async SQLAlchemy engine
engine = create_async_engine(str(settings.database_url), **engine_kwargs)

# Async session factory
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for injecting async DB sessions."""
    async with async_session() as session:
        yield session
