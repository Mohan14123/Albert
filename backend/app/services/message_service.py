"""Business operations for chat messages and AI callbacks."""

from uuid import UUID

from app.core.exceptions import AuthorizationError, NotFoundError
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.services import EventDispatcher


class MessageService:
    def __init__(
        self,
        chats: ChatRepository,
        messages: MessageRepository,
        events: EventDispatcher,
    ) -> None:
        self._chats = chats
        self._messages = messages
        self._events = events

    async def send_message(self, user_id: UUID, chat_id: UUID, content: str):
        await self._require_owned_chat(user_id, chat_id)
        message = await self._messages.create(chat_id, "user", content, "pending")
        await self._events.publish(
            "message.received",
            {
                "message_id": str(message.id),
                "chat_id": str(chat_id),
                "user_id": str(user_id),
            },
        )
        return message

    async def get_messages(self, user_id: UUID, chat_id: UUID, page: int, limit: int):
        await self._require_owned_chat(user_id, chat_id)
        return await self._messages.get_by_chat(chat_id, page, limit)

    async def store_ai_response(
        self, chat_id: UUID, content: str, token_count: int | None
    ):
        chat = await self._chats.get_by_id(chat_id)
        if chat is None:
            raise NotFoundError("Chat not found")
        message = await self._messages.create(
            chat_id, "assistant", content, "completed"
        )
        message.token_count = token_count
        await self._events.publish(
            "message.stored", {"message_id": str(message.id), "chat_id": str(chat_id)}
        )
        return message

    async def _require_owned_chat(self, user_id: UUID, chat_id: UUID):
        chat = await self._chats.get_by_id(chat_id)
        if chat is None:
            raise NotFoundError("Chat not found")
        if chat.user_id != user_id:
            raise AuthorizationError("You do not have access to this chat")
        return chat
