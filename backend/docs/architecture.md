# 01 - System Architecture

**Project:** AI Personal Assistant  
**Version:** 1.0  
**Owner:** Backend Team  
**Last Updated:** 18 July 2026

---

# 1. Overview

This project is a modular AI Personal Assistant designed using a service-oriented, event-driven architecture. The goal is to create a backend that is scalable, maintainable, and extensible while allowing independent development of the Frontend, Backend, and AI systems.

The backend acts as the central platform responsible for:

- Authentication
- User Management
- Chat Management
- API Gateway
- Integrations
- Event Processing
- Database Management
- Communication with the AI Service

The AI system remains an independent module that communicates only through documented APIs and events.

---

# 2. High-Level Architecture

```
                        Client (React / Next.js)
                                 │
                                 │ HTTPS
                                 ▼
                     FastAPI API Gateway
                                 │
     ┌───────────────┬──────────────┬──────────────┐
     │               │              │              │
 Authentication   Chat Service   User Service  Integration Service
     │               │              │              │
     └───────────────┴──────┬───────┴──────────────┘
                            │
                      Event Bus (RabbitMQ)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    AI Service        Background Workers    Notification
        │
        │
 PostgreSQL      Redis      Vector Database (Future)
```

---

# 3. Design Principles

The project follows the following architectural principles.

## Modular

Every feature exists as an independent module.

Example

```
Auth
Chat
Users
Integrations
AI
Memory
Files
```

Each module should be replaceable without affecting the rest of the system.

---

## Event Driven

Heavy operations should never block HTTP requests.

Instead of

```
User uploads file

↓

Backend processes everything
```

Use

```
User uploads file

↓

Event Published

↓

Background Worker

↓

Processing Complete
```

Benefits

- Better scalability
- Better performance
- Loose coupling
- Easier maintenance

---

## Plug-and-Play Integrations

Every external provider follows the same interface.

Example

```
Google

Slack

GitHub

Jira

Notion
```

Each provider implements

```
connect()

disconnect()

refresh()

sync()

webhook()
```

---

## Dependency Injection

Business logic should never depend directly on implementations.

Use interfaces wherever possible.

Example

```
ChatService

↓

LLM Provider Interface

↓

OpenAI

Claude

Gemini

Local Model
```

---

# 4. Backend Components

## API Gateway

Responsible for

- Request validation
- Authentication
- Authorization
- Routing
- Rate limiting
- Logging
- API documentation

---

## Authentication Service

Responsibilities

- Login
- Register
- Refresh Token
- Logout
- OAuth

Uses

- JWT
- Refresh Tokens
- Password Hashing

---

## User Service

Stores

- Profile
- Preferences
- Timezone
- Language
- Assistant Settings
- Connected Integrations

---

## Chat Service

Handles

- Chat creation
- Message storage
- Conversation history
- Streaming responses
- Chat titles

---

## Integration Service

Responsible for

- OAuth
- Token Storage
- Token Refresh
- Sync
- Webhooks

Supported providers

- Gmail
- Google Calendar
- Slack
- Jira
- GitHub
- Notion

Future providers can be added without changing existing code.

---

## Event Bus

Responsible for communication between services.

Example events

```
UserCreated

ChatCreated

MessageReceived

IntegrationConnected

MemoryUpdated
```

---

## Background Workers

Responsible for long-running jobs.

Examples

- Email synchronization
- Calendar synchronization
- Memory compression
- Embedding generation
- File indexing
- Notifications

---

# 5. AI Communication

The backend does not implement AI logic.

Instead

```
User

↓

Backend

↓

AI API

↓

Backend

↓

Client
```

Backend responsibilities

- Store messages
- Build request
- Forward request
- Stream response
- Store response

AI responsibilities

- Planning
- Reasoning
- Tool calling
- Memory retrieval
- RAG
- Response generation

---

# 6. Database Layer

Primary Database

```
PostgreSQL
```

Stores

- Users
- Chats
- Messages
- Integrations
- OAuth Tokens
- Settings

---

## Cache

```
Redis
```

Stores

- Sessions
- Rate limits
- Temporary state
- Streaming cache

---

## Future

Vector Database

```
Qdrant

or

pgvector
```

Stores

- Embeddings
- Semantic search vectors
- Knowledge retrieval

---

# 7. Event Flow

Example

```
User sends message

↓

API Gateway

↓

Authentication

↓

Chat Service

↓

Store Message

↓

Publish Event

↓

AI Service

↓

Generate Response

↓

Store Response

↓

Return Stream
```

---

# 8. Request Flow

```
Client

↓

HTTPS Request

↓

FastAPI Router

↓

Authentication Middleware

↓

Validation

↓

Service Layer

↓

Repository Layer

↓

Database

↓

Response
```

---

# 9. Folder Structure

```
backend/

│

├── app/
│
├── api/
│
├── auth/
│
├── chat/
│
├── users/
│
├── database/
│
├── repositories/
│
├── services/
│
├── integrations/
│
├── events/
│
├── workers/
│
├── middleware/
│
├── core/
│
├── config/
│
├── tests/
│
├── docs/
│
├── scripts/
│
├── alembic/
│
├── Dockerfile
│
├── docker-compose.yml
│
└── requirements.txt
```

---

# 10. Technology Stack

| Layer | Technology |
|---------|------------|
| Backend | FastAPI |
| Language | Python 3.12 |
| Database | PostgreSQL |
| Cache | Redis |
| Event Bus | RabbitMQ |
| ORM | SQLAlchemy |
| Migration | Alembic |
| Authentication | JWT |
| Background Jobs | Celery |
| Containerization | Docker |
| API Documentation | OpenAPI / Swagger |
| Testing | Pytest |
| Linting | Ruff |
| Formatting | Black |
| Type Checking | MyPy |

---

# 11. Security

The backend follows these security principles.

- JWT Authentication
- Refresh Tokens
- Password Hashing (Argon2)
- HTTPS Only
- Rate Limiting
- CORS Protection
- Input Validation
- SQL Injection Protection
- Secrets stored in Environment Variables
- OAuth Token Encryption

---

# 12. Scalability Strategy

The architecture is designed for horizontal scaling.

Future scaling includes

- Multiple FastAPI instances
- Redis Cluster
- RabbitMQ Cluster
- Read Replicas
- Dedicated AI Servers
- Kubernetes Deployment
- CDN
- Object Storage (S3)

No application code should require modification when scaling infrastructure.

---

# 13. Responsibilities

## Backend Team

Responsible for

- APIs
- Database
- Authentication
- Event Bus
- Integrations
- Infrastructure
- Documentation

---

## AI Team

Responsible for

- Planner
- LLM Gateway
- Memory
- RAG
- Tool Calling
- Prompt Management
- Streaming Logic

---

## Frontend Team

Responsible for

- User Interface
- Authentication Screens
- Chat Interface
- History
- API Integration
- Streaming UI

---

# 14. Future Roadmap

Planned additions

- Multi-Agent Architecture
- Voice Assistant
- Real-Time Notifications
- Plugin Marketplace
- Mobile Applications
- Workflow Automation
- Enterprise SSO
- Multi-Tenant Deployment
- Distributed Memory System

---

# 15. Architecture Goals

The architecture is designed to achieve:

- High Performance
- Scalability
- Loose Coupling
- Security
- Maintainability
- Easy Testing
- Easy Deployment
- Independent Team Development
- Plug-and-Play Integrations
- Future AI Expansion

---

**End of Document**