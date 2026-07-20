"""FastAPI application entry-point: wires middleware, routers, and lifecycle hooks."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    auth,
    chats,
    google_auth,
    health,
    integrations,
    memory,
    messages,
    news,
    plugins,
    users,
)
from app.api.webhooks import providers
from app.config.settings import settings
from app.core.logging import LoggingMiddleware
from app.middleware.exception_handler import add_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware, setup_logging
from app.middleware.metrics import SimpleMetricsMiddleware
from app.middleware.rate_limiting import RateLimitingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────
# Application factory
# ──────────────────────────────────────────────────────────


def create_app() -> FastAPI:
    setup_logging()

    # ── Lifecycle hooks ───────────────────────────────────
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Starting Albert backend…")
        # Verify DB connection
        from sqlalchemy import text

        from app.database.engine import engine

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL connection OK")

        # Connect Redis
        try:
            import redis.asyncio as aioredis

            redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
            await redis_client.ping()
            app.state.redis = redis_client
            logger.info("Redis connection OK")
        except Exception as exc:
            logger.warning("Redis not available at startup: %s", exc)
            app.state.redis = None

        # Connect RabbitMQ event publisher
        try:
            from app.events.publisher import EventPublisher

            publisher = EventPublisher()
            await publisher.connect()
            app.state.publisher = publisher
            logger.info("RabbitMQ connection OK")
        except Exception as exc:
            logger.warning("RabbitMQ not available at startup: %s", exc)
            app.state.publisher = None

        logger.info("Albert backend ready on %s:%s", settings.host, settings.port)

        yield  # application is running

        logger.info("Shutting down Albert backend…")
        if getattr(app.state, "publisher", None) is not None:
            await app.state.publisher.close()
            logger.info("RabbitMQ publisher closed")
        if getattr(app.state, "redis", None) is not None:
            await app.state.redis.aclose()
            logger.info("Redis connection closed")
        from app.database.engine import engine

        await engine.dispose()
        logger.info("DB engine disposed")

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Production-grade backend API for Albert AI Personal Assistant.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware (outermost first) ──────────────────────
    app.add_middleware(SecurityHeadersMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestLoggingMiddleware)

    app.add_middleware(SimpleMetricsMiddleware)
    app.add_middleware(LoggingMiddleware)

    if settings.rate_limit_enabled:
        app.add_middleware(RateLimitingMiddleware)

    # ── Exception handlers ────────────────────────────────
    add_exception_handlers(app)

    # ── Routers ───────────────────────────────────────────
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(google_auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(chats.router, prefix="/api/v1")
    app.include_router(messages.router, prefix="/api/v1")
    app.include_router(memory.router, prefix="/api/v1")
    app.include_router(plugins.router, prefix="/api/v1")
    app.include_router(integrations.router, prefix="/api/v1")
    app.include_router(news.router, prefix="/api/v1")
    app.include_router(providers.router, prefix="/webhooks")

    return app


app = create_app()
