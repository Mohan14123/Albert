"""Business operations for user-owned chats."""

from uuid import UUID

from app.core.exceptions import AuthorizationError, NotFoundError
from app.repositories.chat_repository import ChatRepository
from app.services import EventDispatcher


class ChatService:
    def __init__(self, chats: ChatRepository, events: EventDispatcher) -> None:
        self._chats = chats
        self._events = events

    async def create_chat(self, user_id: UUID, title: str):
        chat = await self._chats.create(user_id, title)
        await self._events.publish(
            "chat.created", {"chat_id": str(chat.id), "user_id": str(user_id)}
        )
        return chat

    async def get_chats(self, user_id: UUID, page: int, limit: int):
        return await self._chats.get_by_user(user_id, page, limit)

    async def get_chat(self, user_id: UUID, chat_id: UUID):
        chat = await self._require_owned_chat(user_id, chat_id)
        return chat

    async def rename_chat(self, user_id: UUID, chat_id: UUID, title: str):
        await self._require_owned_chat(user_id, chat_id)
        chat = await self._chats.update(chat_id, {"title": title})
        if chat is None:
            raise NotFoundError("Chat not found")
        return chat

    async def delete_chat(self, user_id: UUID, chat_id: UUID) -> None:
        await self._require_owned_chat(user_id, chat_id)
        await self._chats.soft_delete(chat_id)
        await self._events.publish(
            "chat.deleted", {"chat_id": str(chat_id), "user_id": str(user_id)}
        )

    async def _require_owned_chat(self, user_id: UUID, chat_id: UUID):
        chat = await self._chats.get_by_id(chat_id)
        if chat is None:
            raise NotFoundError("Chat not found")
        if chat.user_id != user_id:
            raise AuthorizationError("You do not have access to this chat")
        return chat
