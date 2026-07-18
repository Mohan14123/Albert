# 06 - Event Bus Architecture

**Project:** AI Personal Assistant  
**Version:** 1.0  
**Owner:** Backend Team  
**Message Broker:** RabbitMQ  
**Pattern:** Event-Driven Architecture (EDA)  
**Last Updated:** 18 July 2026

---

# 1. Purpose

This document defines the event-driven architecture used throughout the backend.

The event bus enables independent services to communicate without directly depending on one another.

Benefits include:

- Loose coupling
- Better scalability
- Easier maintenance
- Background processing
- Fault tolerance
- Future microservice compatibility

---

# 2. Architecture Overview

```
                   Client
                      │
                      ▼
                 FastAPI API
                      │
              Business Service
                      │
             Publish Domain Event
                      │
                 RabbitMQ Exchange
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    AI Worker   Integration Worker  Notification Worker
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                 Database Update
```

---

# 3. Event Flow

Example

```
User Sends Message

↓

ChatService

↓

Save Message

↓

Publish MessageReceived

↓

RabbitMQ

↓

AI Worker

↓

Generate Response

↓

Publish AIResponseGenerated

↓

Chat Worker

↓

Save Response

↓

Notify Client
```

---

# 4. Event Components

Every event contains:

```
Producer

Exchange

Routing Key

Payload

Consumer

Acknowledgement
```

---

# 5. Event Structure

Every event follows the same schema.

```json
{
  "event_id": "uuid",
  "event_name": "MessageReceived",
  "version": "1.0",
  "timestamp": "2026-07-18T12:30:00Z",
  "producer": "ChatService",
  "correlation_id": "uuid",
  "payload": {}
}
```

---

# 6. Event Metadata

| Field | Description |
|---------|-------------|
| event_id | Unique event identifier |
| event_name | Event type |
| version | Event schema version |
| timestamp | UTC timestamp |
| producer | Service that published event |
| correlation_id | Links related events |
| payload | Business data |

---

# 7. Exchanges

RabbitMQ exchanges

```
domain.exchange

integration.exchange

notification.exchange

system.exchange
```

---

# 8. Routing Keys

Convention

```
domain.entity.action
```

Examples

```
user.created

user.updated

chat.created

chat.deleted

message.received

message.generated

integration.connected

integration.synced

notification.created
```

---

# 9. Domain Events

## User Events

```
UserCreated

UserUpdated

UserDeleted
```

Producer

```
UserService
```

Consumers

```
Analytics

Notification

AI Service
```

---

## Chat Events

```
ChatCreated

ChatArchived

ChatDeleted
```

Producer

```
ChatService
```

Consumers

```
Analytics

AI
```

---

## Message Events

```
MessageReceived

MessageStored

MessageFailed

AIResponseGenerated
```

Producer

```
ChatService

AI Service
```

Consumers

```
AI Worker

Notification

History Worker
```

---

## Integration Events

```
IntegrationConnected

IntegrationDisconnected

IntegrationExpired

IntegrationSynced
```

Producer

```
IntegrationService
```

Consumers

```
Sync Worker

Notification

Analytics
```

---

## Authentication Events

```
UserLoggedIn

UserLoggedOut

TokenRefreshed

PasswordChanged
```

Consumers

```
Audit

Analytics

Security
```

---

# 10. Future Events

```
MemoryUpdated

FileUploaded

EmbeddingGenerated

ReminderCreated

VoiceProcessed

CalendarSynced

EmailIndexed
```

---

# 11. Event Producers

| Service | Events |
|----------|--------|
| Auth Service | Login, Logout |
| User Service | User Created |
| Chat Service | Chat Created, Message Received |
| Integration Service | Connected, Synced |
| AI Service | AI Response Generated |

---

# 12. Event Consumers

AI Worker

Consumes

```
MessageReceived
```

---

Notification Worker

Consumes

```
IntegrationConnected

ReminderCreated

UserCreated
```

---

History Worker

Consumes

```
MessageStored

AIResponseGenerated
```

---

Analytics Worker

Consumes

```
All business events
```

---

# 13. Retry Strategy

If processing fails

```
Receive Event

↓

Failure

↓

Retry Queue

↓

Retry

↓

Success

OR

Dead Letter Queue
```

Retry policy

```
Attempt 1

↓

Attempt 2

↓

Attempt 3

↓

Dead Letter Queue
```

---

# 14. Dead Letter Queue

Every exchange has a DLQ.

Example

```
message.dlq

integration.dlq

notification.dlq
```

Reasons

- Invalid payload
- Consumer crash
- External API unavailable
- Unexpected exception

---

# 15. Event Ordering

Ordering is guaranteed only within the same entity.

Example

```
Chat A

Message 1

↓

Message 2

↓

Message 3
```

Ordering between unrelated entities is not guaranteed.

---

# 16. Idempotency

Consumers must safely process duplicate events.

Every event contains

```
event_id
```

Consumers store processed IDs.

If already processed

```
Ignore Event
```

---

# 17. Correlation IDs

Each request generates

```
correlation_id
```

Example

```
User Request

↓

MessageReceived

↓

AIResponseGenerated

↓

NotificationSent
```

All events share the same correlation ID.

---

# 18. Event Versioning

Schema version

```
version = 1.0
```

Breaking changes

```
2.0
```

Never modify existing payloads without versioning.

---

# 19. Payload Guidelines

Payloads should include only necessary business data.

Good

```json
{
  "chat_id": "uuid",
  "message_id": "uuid"
}
```

Avoid

```json
{
  "entire_chat_history": "..."
}
```

Consumers should fetch additional data if needed.

---

# 20. Logging

Every published event logs

- Event ID
- Correlation ID
- Producer
- Consumer
- Processing time
- Status

Example

```
Published

MessageReceived

ID

12345

Duration

8ms
```

---

# 21. Monitoring Metrics

Track

- Events Published
- Events Consumed
- Queue Length
- Failed Events
- Retry Count
- Processing Latency
- Dead Letter Count

Expose metrics through Prometheus.

---

# 22. Queue Naming

Convention

```
<domain>.<consumer>.queue
```

Examples

```
chat.ai.queue

chat.history.queue

integration.sync.queue

notification.email.queue

analytics.events.queue
```

---

# 23. Folder Structure

```
app/events/

├── publisher.py
├── consumer.py
├── exchanges.py
├── routing.py
├── schemas.py
├── handlers/
│   ├── chat.py
│   ├── auth.py
│   ├── integration.py
│   └── notification.py
└── workers/
```

---

# 24. Best Practices

- Publish events only after successful database transactions (Outbox pattern recommended).
- Keep payloads small.
- Make consumers idempotent.
- Use correlation IDs for tracing.
- Version every event schema.
- Use retry queues for transient failures.
- Send unrecoverable failures to a dead letter queue.
- Avoid direct service-to-service calls when an event is sufficient.
- Do not perform long-running tasks inside HTTP request handlers.

---

# 25. Example Event Lifecycle

```
POST /chats/{id}/messages

↓

Message Stored

↓

MessageReceived Event

↓

RabbitMQ

↓

AI Worker

↓

AIResponseGenerated Event

↓

Chat Worker

↓

Assistant Message Stored

↓

Frontend Streams Response
```

---

# 26. Definition of Done

The event system is complete when:

- RabbitMQ is configured.
- Exchanges and queues are created automatically.
- All domain events follow the standard schema.
- Producers publish events only after successful transactions.
- Consumers are idempotent.
- Retry queues and dead letter queues are implemented.
- Correlation IDs enable end-to-end tracing.
- Metrics and structured logs are available.
- The AI, integration, and notification services communicate exclusively through documented events where appropriate.

---

**End of Document**