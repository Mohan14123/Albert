from fastapi import APIRouter
from typing import Any

router = APIRouter(tags=["health"])

@router.get("/health")
async def health() -> Any:
    return {"status": "healthy"}

@router.get("/ready")
async def ready() -> Any:
    return {"status": "ready"}

@router.get("/version")
async def version() -> Any:
    return {"version": "1.0.0"}
