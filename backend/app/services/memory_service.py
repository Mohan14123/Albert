import base64
import logging
from collections.abc import Sequence
from uuid import UUID

import httpx
from cryptography.fernet import Fernet

from app.config.settings import settings
from app.database.models.memory import Memory
from app.repositories.memory_repository import MemoryRepository
from app.services import EventDispatcher

logger = logging.getLogger(__name__)


class MemoryService:
    def __init__(self, memories: MemoryRepository, events: EventDispatcher) -> None:
        self._memories = memories
        self._events = events
        key = settings.token_encryption_key.get_secret_value()
        # pad to 32 bytes and urlsafe base64 encode for fernet
        padded_key = key.ljust(32, "0")[:32].encode("utf-8")
        self._fernet = Fernet(base64.urlsafe_b64encode(padded_key))

    def _encrypt(self, text: str) -> str:
        return self._fernet.encrypt(text.encode()).decode()

    def _decrypt(self, text: str) -> str:
        try:
            return self._fernet.decrypt(text.encode()).decode()
        except Exception:
            return text  # fallback for unencrypted existing memories

    async def _get_embedding(self, text: str) -> list[float]:
        if not settings.ai_api_key:
            return [0.0] * 1536
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {settings.ai_api_key.get_secret_value()}"
                    },
                    json={"input": text, "model": "text-embedding-3-small"},
                )
                resp.raise_for_status()
                return resp.json()["data"][0]["embedding"]
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                return [0.0] * 1536

    async def store_memory(
        self, user_id: UUID, content: str, category: str | None = None
    ) -> Memory:
        encrypted_content = self._encrypt(content)
        memory = await self._memories.create(user_id, encrypted_content, category)
        embedding = await self._get_embedding(content)
        memory.embedding = embedding  # type: ignore
        # Assume caller will commit, or the repository handles it
        # The original code just did create() which flushes, we should set embedding.
        await self._events.publish(
            "memory.stored",
            {
                "user_id": str(user_id),
                "memory_id": str(memory.id),
                "category": category,
            },
        )
        # return memory with decrypted content so callers see plaintext
        memory.content = content  # type: ignore
        return memory

    async def get_all_for_user(self, user_id: UUID) -> Sequence[Memory]:
        memories = await self._memories.get_all_for_user(user_id)
        for m in memories:
            m.content = self._decrypt(str(m.content))  # type: ignore
        return memories

    async def search_memories(
        self, user_id: UUID, query: str, limit: int = 5
    ) -> Sequence[Memory]:
        query_embedding = await self._get_embedding(query)
        memories = await self._memories.search_by_vector(
            user_id, query_embedding, limit
        )
        for m in memories:
            m.content = self._decrypt(str(m.content))  # type: ignore
        return memories

    async def compress_memories(self, user_id: UUID) -> None:
        # Stub for background memory compression task
        logger.info(f"Compressing memories for user {user_id}")

    async def cleanup_expired(self) -> None:
        # Stub for expired memory cleanup
        logger.info("Cleaning up expired memories")
