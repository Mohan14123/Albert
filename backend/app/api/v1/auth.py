from fastapi import APIRouter
from typing import Any
from app.api.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, UserResponse
from uuid import uuid4
from datetime import datetime, UTC

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(request: RegisterRequest) -> Any:
    return {"success": True, "data": {"user_id": str(uuid4())}}

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> Any:
    return {"access_token": "token", "refresh_token": "refresh", "expires_in": 900}

@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest) -> Any:
    return {"access_token": "new_token", "refresh_token": "new_refresh", "expires_in": 900}

@router.post("/logout")
async def logout() -> Any:
    return {"success": True}

@router.post("/logout-all")
async def logout_all() -> Any:
    return {"success": True}

@router.get("/me", response_model=UserResponse)
async def me() -> Any:
    return {"id": uuid4(), "email": "test@test.com", "full_name": "Test User", "assistant_name": "Albert", "is_active": True}
