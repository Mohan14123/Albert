"""News API endpoints for retrieving current headlines and search topics."""

import logging
from typing import Any
from fastapi import APIRouter, Query

from app.integrations.news.service import NewsIntegration

logger = logging.getLogger(__name__)

router = APIRouter(tags=["news"])
_news_service = NewsIntegration()


@router.get("/news")
async def get_news(
    category: str = Query(default="general", description="Category: technology, ai, business, world, general"),
    limit: int = Query(default=5, ge=1, le=20, description="Number of headlines"),
) -> dict[str, Any]:
    """Get live top headlines filtered by category."""
    headlines = await _news_service.get_headlines(category=category, limit=limit)
    return {
        "status": "success",
        "category": category,
        "count": len(headlines),
        "headlines": headlines,
    }
