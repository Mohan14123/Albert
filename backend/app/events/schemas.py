"""Versioned wire schema for domain events."""

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Portable event envelope shared by every asynchronous consumer."""

    event_name: str
    payload: dict[str, Any]
    event_id: UUID = field(default_factory=uuid4)
    version: str = "1.0"
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    producer: str = "backend"
    correlation_id: UUID = field(default_factory=uuid4)

    def to_json(self) -> str:
        data = asdict(self)
        data["event_id"] = str(self.event_id)
        data["correlation_id"] = str(self.correlation_id)
        data["timestamp"] = self.timestamp.isoformat()
        return json.dumps(data, default=str, separators=(",", ":"))

    @classmethod
    def from_json(cls, raw_event: str | bytes) -> "DomainEvent":
        data = json.loads(raw_event)
        return cls(
            event_id=UUID(data["event_id"]),
            event_name=data["event_name"],
            version=data["version"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            producer=data["producer"],
            correlation_id=UUID(data["correlation_id"]),
            payload=data["payload"],
        )
