import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SimpleMetricsMiddleware(BaseHTTPMiddleware):
    # Basic in-memory metrics
    request_count = 0
    total_time = 0.0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        type(self).request_count += 1
        type(self).total_time += process_time

        return response

    @classmethod
    def get_metrics(cls) -> dict:
        return {
            "total_requests": cls.request_count,
            "total_time_seconds": cls.total_time,
            "average_time_seconds": (
                (cls.total_time / cls.request_count) if cls.request_count > 0 else 0
            ),
        }
