"""Database seeder — creates test user, chats, and messages for local development."""

import asyncio
import logging

from app.config.settings import settings
from app.core.security import get_password_hash
from app.database.models.chat import Chat
from app.database.models.message import Message
from app.database.models.user import User
from app.database.models.user_settings import UserSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_EMAIL = "test@albert.dev"
TEST_PASSWORD = "TestPassword@123"
TEST_NAME = "Albert Test User"


async def seed_db() -> None:
    engine = create_async_engine(str(settings.database_url), echo=False)
    async_session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session_factory() as session, session.begin():
        # ── Create test user ────────────────────────────────
        from sqlalchemy import select

        existing = await session.scalar(select(User).where(User.email == TEST_EMAIL))
        if existing:
            logger.info("Test user already exists — skipping user creation")
            user = existing
        else:
            user = User(
                email=TEST_EMAIL,
                password_hash=get_password_hash(TEST_PASSWORD),
                full_name=TEST_NAME,
                assistant_name="Albert",
                timezone="UTC",
                language="en",
            )
            session.add(user)
            await session.flush()
            logger.info("Created test user: %s (id=%s)", TEST_EMAIL, user.id)

            # Default settings
            user_settings = UserSettings(
                user_id=user.id,
                theme="dark",
                language="en",
                notifications=True,
            )
            session.add(user_settings)

        # ── Create sample chats with messages ───────────────
        sample_chats = [
            {
                "title": "Welcome Chat",
                "messages": [
                    ("user", "Hello Albert! Can you help me?"),
                    (
                        "assistant",
                        "Of course! I'm Albert, your AI assistant. How can I help you today?",
                    ),
                ],
            },
            {
                "title": "Project Planning",
                "messages": [
                    ("user", "Help me plan my week."),
                    (
                        "assistant",
                        "Sure! Let's start by listing your top priorities for this week.",
                    ),
                    ("user", "I need to finish the backend and review the frontend."),
                ],
            },
            {
                "title": "Gmail Integration Test",
                "messages": [
                    ("user", "Can you check my emails?"),
                    (
                        "assistant",
                        "I'll need access to your Gmail first. Please connect your Google account in the integrations section.",
                    ),
                ],
            },
        ]

        for chat_data in sample_chats:
            existing_chat = await session.scalar(
                select(Chat).where(
                    Chat.user_id == user.id, Chat.title == chat_data["title"]
                )
            )
            if existing_chat:
                logger.info("Chat '%s' already exists — skipping", chat_data["title"])
                continue

            chat = Chat(user_id=user.id, title=chat_data["title"])
            session.add(chat)
            await session.flush()

            for role, content in chat_data["messages"]:
                message = Message(
                    chat_id=chat.id,
                    role=role,
                    content=content,
                    status="completed",
                )
                session.add(message)

            logger.info(
                "Created chat '%s' with %d messages",
                chat_data["title"],
                len(chat_data["messages"]),
            )

    await engine.dispose()
    logger.info(
        "\n✅ Seeding complete!\n"
        "   Email:    %s\n"
        "   Password: %s\n"
        "   Chats:    %d created",
        TEST_EMAIL,
        TEST_PASSWORD,
        len(sample_chats),
    )


if __name__ == "__main__":
    asyncio.run(seed_db())
