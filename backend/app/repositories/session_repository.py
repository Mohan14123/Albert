from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.session import Session


class SessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        user_id: UUID,
        refresh_token_id: UUID | None,
        ip_address: str | None,
        user_agent: str | None,
        expires_at: datetime,
    ) -> Session:
        session_obj = Session(
            user_id=user_id,
            refresh_token_id=refresh_token_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True,
        )
        self._session.add(session_obj)
        await self._session.commit()
        await self._session.refresh(session_obj)
        return session_obj

    async def get_by_id(self, session_id: UUID) -> Session | None:
        return await self._session.get(Session, session_id)

    async def get_active_sessions(self, user_id: UUID) -> Sequence[Session]:
        stmt = (
            select(Session)
            .where(
                Session.user_id == user_id,
                Session.is_active == True,
                Session.expires_at > datetime.now(UTC),
            )
            .order_by(Session.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def revoke(self, session_id: UUID) -> None:
        stmt = update(Session).where(Session.id == session_id).values(is_active=False)
        await self._session.execute(stmt)
        await self._session.commit()

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        stmt = (
            update(Session)
            .where(Session.user_id == user_id, Session.is_active == True)
            .values(is_active=False)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount
