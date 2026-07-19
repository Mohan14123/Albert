from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.database.models.user import User
from app.events.publisher import EventPublisher
from app.repositories.memory_repository import MemoryRepository
from app.services.events import EventDispatcher
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])


def _get_memory_service(db: AsyncSession = Depends(get_db)) -> MemoryService:
    return MemoryService(
        memories=MemoryRepository(db),
        events=EventDispatcher(EventPublisher()),
    )


@router.get("")
async def get_memories(
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(_get_memory_service),
) -> dict:
    """Retrieve all memories for the authenticated user."""
    memories = await service.get_all_for_user(current_user.id)
    return success_response(
        {
            "items": [
                {
                    "id": m.id,
                    "content": m.content,
                    "category": m.category,
                    "relevance_score": m.relevance_score,
                    "created_at": m.created_at,
                }
                for m in memories
            ]
        }
    )


@router.get("/search")
async def search_memories(
    q: str,
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(_get_memory_service),
) -> dict:
    """Search user memories."""
    memories = await service.search_memories(current_user.id, q)
    return success_response(
        {
            "items": [
                {
                    "id": m.id,
                    "content": m.content,
                    "category": m.category,
                    "relevance_score": m.relevance_score,
                    "created_at": m.created_at,
                }
                for m in memories
            ]
        }
    )
