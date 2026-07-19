from typing import Any
from uuid import UUID

from app.database.engine import async_session
from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    @staticmethod
    async def log_action(
        action: str,
        user_id: UUID | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        ip_address: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log an audit event asynchronously."""
        async with async_session() as session:
            repository = AuditLogRepository(session)
            await repository.create(
                action=action,
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
                metadata=metadata,
            )
