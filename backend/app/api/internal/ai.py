from fastapi import APIRouter
from typing import Any
from pydantic import BaseModel

class AIRespondRequest(BaseModel):
    message: str

class AICallbackRequest(BaseModel):
    content: str
    token_count: int

router = APIRouter(prefix="/ai", tags=["internal-ai"])

@router.post("/respond")
async def ai_respond(request: AIRespondRequest) -> Any:
    return {"success": True}

@router.post("/callback")
async def ai_callback(request: AICallbackRequest) -> Any:
    return {"success": True}
