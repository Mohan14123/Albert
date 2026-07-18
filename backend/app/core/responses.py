from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response wrapper."""
    success: bool = True
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""
    success: bool = False
    error_code: str
    message: str


class PaginatedData(BaseModel, Generic[T]):
    """Pagination metadata and data."""
    items: list[T]
    page: int
    limit: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper."""
    success: bool = True
    data: PaginatedData[T]


def success_response(data: Any = None) -> dict[str, Any]:
    """Helper to return a success dictionary."""
    return {"success": True, "data": data}


def error_response(code: str, message: str) -> dict[str, Any]:
    """Helper to return an error dictionary."""
    return {"success": False, "error_code": code, "message": message}


def paginated_response(items: list[Any], page: int, limit: int, total: int) -> dict[str, Any]:
    """Helper to return a paginated dictionary."""
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    return {
        "success": True,
        "data": {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
        }
    }
