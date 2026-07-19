"""Base consumer for RabbitMQ domain events."""

import abc
import asyncio
import logging
from typing import Any
from uuid import UUID

import aio_pika
import redis.asyncio as redis

from app.config.settings import settings
from app.events.publisher import EventPublisher
from app.events.schemas import DomainEvent
from app.events.exchanges import DOMAIN_EXCHANGE, EXCHANGE_TYPE

logger = logging.getLogger(__name__)

class BaseConsumer(abc.ABC):
    """Base RabbitMQ consumer with idempotency and retry logic."""

    def __init__(
        self,
        queue_name: str,
        routing_key: str,
        exchange_name: str = DOMAIN_EXCHANGE,
        max_retries: int = 3,
    ) -> None:
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.exchange_name = exchange_name
        self.max_retries = max_retries
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._redis: redis.Redis | None = None
        self._publisher: EventPublisher = EventPublisher()

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=10)
        
        exchange = await self._channel.declare_exchange(
            self.exchange_name, aio_pika.ExchangeType(EXCHANGE_TYPE), durable=True
        )
        
        dlq_name = f"{self.exchange_name.split('.')[0]}.dlq"
        dlx_name = f"{dlq_name}.exchange"
        
        dlx = await self._channel.declare_exchange(dlx_name, aio_pika.ExchangeType.DIRECT, durable=True)
        dlq = await self._channel.declare_queue(dlq_name, durable=True)
        await dlq.bind(dlx, routing_key=self.queue_name)

        queue = await self._channel.declare_queue(
            self.queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": dlx_name,
                "x-dead-letter-routing-key": self.queue_name,
            },
        )
        await queue.bind(exchange, routing_key=self.routing_key)
        
        self._redis = redis.from_url(settings.redis_url)
        await self._publisher.connect()

        await queue.consume(self._process_message)
        logger.info("Started consuming from %s (routing_key: %s)", self.queue_name, self.routing_key)

    async def start(self) -> None:
        """Connect and run indefinitely until interrupted."""
        await self.connect()
        try:
            await asyncio.Future()  # block forever
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            await self.close()

    async def _process_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process(requeue=False, ignore_processed=True):
            try:
                event = DomainEvent.from_json(message.body)
                
                # Check idempotency
                idempotency_key = f"processed_event:{event.event_id}"
                if self._redis and await self._redis.exists(idempotency_key):
                    logger.info("Event %s already processed, skipping", event.event_id)
                    await message.ack()
                    return

                await self.on_message(event)
                
                # Mark as processed (TTL 24 hours)
                if self._redis:
                    await self._redis.setex(idempotency_key, 86400, "1")
                
                await message.ack()

            except Exception as e:
                logger.exception("Error processing message %s: %s", message.message_id, e)
                
                # Retry logic
                headers = message.headers or {}
                retry_count = headers.get("x-retry-count", 0)
                
                if isinstance(retry_count, int) and retry_count < self.max_retries:
                    logger.info("Retrying message %s (attempt %d/%d)", message.message_id, retry_count + 1, self.max_retries)
                    new_headers = dict(headers)
                    new_headers["x-retry-count"] = retry_count + 1
                    
                    new_message = aio_pika.Message(
                        body=message.body,
                        headers=new_headers,
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    )
                    assert self._channel is not None
                    await self._channel.default_exchange.publish(
                        new_message,
                        routing_key=self.queue_name,
                    )
                    await message.ack()
                else:
                    logger.error("Max retries reached for message %s, sending to DLQ", message.message_id)
                    await message.reject(requeue=False)

    @abc.abstractmethod
    async def on_message(self, event: DomainEvent) -> None:
        """Process the domain event."""
        pass

    async def close(self) -> None:
        if self._publisher:
            await self._publisher.close()
        if self._connection:
            await self._connection.close()
        if self._redis:
            await self._redis.aclose()
