import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from redis.asyncio import Redis, from_url

from app.config.settings import settings
from app.core.exceptions import RateLimitedError
from app.core.responses import error_response

# Global redis client (initialized in main.py lifespan)
redis_client: Redis | None = None


async def get_redis_client() -> Redis:
    """Get or initialize the redis client."""
    global redis_client
    if not redis_client:
        redis_client = from_url(settings.redis_url)
    return redis_client


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to rate limit requests based on IP or User ID using Redis.
    Limits:
    - Auth endpoints (/api/v1/auth/*): 5 requests per minute per IP
    - Other endpoints: 100 requests per minute per User ID (or IP if unauthenticated)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.rate_limit_enabled:
            return await call_next(request)

        path = request.url.path
        client_ip = request.client.host if request.client else "unknown_ip"
        user_id = getattr(request.state, "user_id", None)

        # Determine limits based on route
        if path.startswith("/api/v1/auth"):
            key = f"rate_limit:auth:{client_ip}"
            limit = 5
            window = 60
        else:
            identifier = user_id if user_id else client_ip
            key = f"rate_limit:api:{identifier}"
            limit = 100
            window = 60

        # Enforce rate limit
        try:
            redis = await get_redis_client()
            
            # Atomic increment and expire
            async with redis.pipeline(transaction=True) as pipe:
                pipe.incr(key)
                pipe.ttl(key)
                results = await pipe.execute()
                
            current_count = results[0]
            ttl = results[1]
            
            if ttl == -1: # No expiration set
                await redis.expire(key, window)
                
            if current_count > limit:
                import json
                return Response(
                    content=json.dumps(error_response("RATE_LIMIT_EXCEEDED", "Too many requests")),
                    status_code=429,
                    media_type="application/json",
                    headers={"Retry-After": str(ttl if ttl > 0 else window)}
                )
                
        except Exception as e:
            import logging
            logger = logging.getLogger("app.access")
            logger.error(f"Rate limiter error: {e}")
            # If redis fails, we fail open (allow the request)
            
        response = await call_next(request)
        return response
