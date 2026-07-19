import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import BaseAppException
from app.core.responses import error_response

logger = logging.getLogger("app.exceptions")


def add_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers to the FastAPI app."""

    @app.exception_handler(BaseAppException)
    async def custom_app_exception_handler(
        request: Request, exc: BaseAppException
    ) -> JSONResponse:
        """Handle our custom application exceptions gracefully."""
        # Convert exception class name to an error code (e.g., NotFoundError -> NOT_FOUND_ERROR)
        error_code = _camel_to_snake(exc.__class__.__name__).upper()

        # We don't log typical 40x errors as exceptions to reduce noise, just info/warning
        if exc.status_code >= 500:
            logger.error(f"Application error: {exc.message}", exc_info=exc)
        else:
            logger.warning(f"Client error ({exc.status_code}): {exc.message}")

        return JSONResponse(
            status_code=exc.status_code, content=error_response(error_code, exc.message)
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        errors = exc.errors()
        # Create a simplified message from the first error
        msg = (
            f"{errors[0]['msg']} (at {'.'.join(str(loc) for loc in errors[0]['loc'])})"
            if errors
            else "Validation failed"
        )

        logger.warning(f"Validation error: {msg}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("VALIDATION_ERROR", msg),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle standard HTTP exceptions."""
        logger.warning(f"HTTP error ({exc.status_code}): {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response("HTTP_ERROR", str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Fallback for all unhandled exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                "INTERNAL_SERVER_ERROR", "An unexpected error occurred."
            ),
        )


def _camel_to_snake(name: str) -> str:
    import re

    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
