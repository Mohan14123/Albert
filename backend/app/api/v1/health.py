"""Health, readiness, and version endpoints."""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Basic liveness check — always returns 200 if the process is running."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/ready")
async def ready() -> JSONResponse:
    """
    Readiness check — verifies connectivity to PostgreSQL, Redis, and RabbitMQ.
    Returns 200 if all dependencies are reachable, 503 otherwise.
    """
    checks: dict[str, str] = {}
    all_ok = True

    # ── PostgreSQL ─────────────────────────────────────────
    try:
        from sqlalchemy import text

        from app.database.engine import engine

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as exc:
        logger.warning("Readiness check — Postgres failed: %s", exc)
        checks["postgres"] = "error"
        all_ok = False

    # ── Redis ──────────────────────────────────────────────
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.redis_url, decode_responses=True)
        await r.ping()
        await r.aclose()
        checks["redis"] = "ok"
    except Exception as exc:
        logger.warning("Readiness check — Redis failed: %s", exc)
        checks["redis"] = "error"
        all_ok = False

    # ── RabbitMQ ───────────────────────────────────────────
    try:
        import aio_pika

        conn = await aio_pika.connect_robust(settings.rabbitmq_url, timeout=3)
        await conn.close()
        checks["rabbitmq"] = "ok"
    except Exception as exc:
        logger.warning("Readiness check — RabbitMQ failed: %s", exc)
        checks["rabbitmq"] = "error"
        all_ok = False

    status_code = 200 if all_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if all_ok else "degraded", "checks": checks},
    )


@router.get("/version")
async def version() -> dict:
    """Return the current application version."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/metrics")
async def metrics() -> dict:
    """Return simple application metrics."""
    from app.middleware.metrics import SimpleMetricsMiddleware

    return SimpleMetricsMiddleware.get_metrics()
