import json
import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.access")


class StructuredLogFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        # Add custom attributes if they exist
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "method"):
            log_obj["method"] = record.method
        if hasattr(record, "path"):
            log_obj["path"] = record.path
        if hasattr(record, "status_code"):
            log_obj["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        if hasattr(record, "client_ip"):
            log_obj["client_ip"] = record.client_ip

        return json.dumps(log_obj)


def setup_logging():
    """Initialize structured logging."""
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredLogFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log requests, calculate duration, and inject Request ID."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract Request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Attach request_id to request state so other parts of the app can use it
        request.state.request_id = request_id

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log the success request
            logger.info(
                f"{request.method} {request.url.path} {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                    "client_ip": request.client.host if request.client else None,
                },
            )

            # Inject Request ID into response headers
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log the failed request
            logger.error(
                f"{request.method} {request.url.path} 500 - {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration_ms": round(duration_ms, 2),
                    "client_ip": request.client.host if request.client else None,
                },
                exc_info=True,
            )
            raise
