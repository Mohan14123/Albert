from fastapi import APIRouter
from typing import Any

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/gmail")
async def gmail_webhook() -> Any:
    return {"success": True}

@router.post("/calendar")
async def calendar_webhook() -> Any:
    return {"success": True}

@router.post("/slack")
async def slack_webhook() -> Any:
    return {"success": True}

@router.post("/jira")
async def jira_webhook() -> Any:
    return {"success": True}
