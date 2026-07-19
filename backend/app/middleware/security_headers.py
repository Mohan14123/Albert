from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to inject standard security headers into all responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Prevent browsers from MIME-sniffing a response away from the declared content-type
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking by ensuring the content is not embedded into other sites
        response.headers["X-Frame-Options"] = "DENY"

        # Control how much referrer information (sent with the Referer header) should be included with requests
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Basic Content-Security-Policy (can be overridden or expanded per endpoint if needed)
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Force HTTPS for 1 year, including subdomains
        # Note: In development this might be annoying if developing over HTTP,
        # so you might conditionally apply it based on environment settings.
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        return response
