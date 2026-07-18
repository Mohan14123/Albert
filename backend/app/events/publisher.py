"""Resilient RabbitMQ publisher for domain events."""

import logging
from collections.abc import Mapping
from uuid import UUID, uuid4

import aio_pika

from app.config.settings import settings
from app.events.exchanges import DOMAIN_EXCHANGE, EXCHANGE_TYPE
from app.events.schemas import DomainEvent

logger = logging.getLogger(__name__)


class EventPublisher:
    """Lazily connects and publishes persistent, correlation-aware events."""

    def __init__(self) -> None:
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def connect(self) -> None:
        if self._exchange is not None:
            return
        self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            DOMAIN_EXCHANGE, aio_pika.ExchangeType(EXCHANGE_TYPE), durable=True
        )

    async def publish(
        self,
        routing_key: str,
        payload: Mapping[str, object],
        *,
        correlation_id: UUID | None = None,
    ) -> None:
        await self.connect()
        assert self._exchange is not None
        event = DomainEvent(
            event_name=routing_key,
            payload=dict(payload),
            correlation_id=correlation_id or uuid4(),
        )
        message = aio_pika.Message(
            event.to_json().encode(),
            content_type="application/json",
            correlation_id=str(event.correlation_id),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await self._exchange.publish(message, routing_key=routing_key)
        logger.info("Published event %s using %s", event.event_id, routing_key)

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
        self._connection = self._channel = self._exchange = None
