# 02 - Backend Architecture

**Project:** AI Personal Assistant  
**Document Version:** 1.0  
**Owner:** Backend Team  
**Last Updated:** 18 July 2026

---

# 1. Purpose

This document describes the internal architecture of the backend system.

The backend is responsible for:

- Authentication
- User Management
- Chat Management
- Database Access
- Event Publishing
- External Integrations
- Communication with the AI Service
- Security
- Infrastructure

The backend **does not implement AI reasoning or memory logic**. It only provides the platform and APIs that the AI service consumes.

---

# 2. Backend Architecture

```
                    Client
                       │
                HTTPS Request
                       │
                       ▼
                FastAPI Application
                       │
        ┌──────────────┴──────────────┐
        │                             │
   Middleware Layer             API Routers
                                      │
                                      ▼
                               Service Layer
                                      │
                     ┌────────────────┴───────────────┐
                     │                                │
              Repository Layer                  Event Publisher
                     │                                │
                     ▼                                ▼
               PostgreSQL                     RabbitMQ Event Bus
                     │                                │
                     └──────────────┬─────────────────┘
                                    │
                              Background Workers
                                    │
                                    ▼
                              External Services
```

---

# 3. Architectural Layers

The backend follows a layered architecture to separate responsibilities.

## Layer 1 – API Layer

Responsible for exposing REST endpoints.

Responsibilities:

- Accept HTTP requests
- Validate input
- Return responses
- Dependency Injection
- Authentication

Folder

```
app/api/
```

Example

```
POST /auth/login

↓

Auth Router

↓

Auth Service
```

The API layer should never contain business logic.

---

## Layer 2 – Service Layer

Contains all business logic.

Responsibilities

- User operations
- Authentication
- Chat management
- Integration management
- Event publishing

Folder

```
app/services/
```

Example

```
Create Chat

↓

Validate Request

↓

Create Database Record

↓

Publish Event

↓

Return Result
```

Services never interact directly with HTTP.

---

## Layer 3 – Repository Layer

Responsible only for database communication.

Responsibilities

- Insert
- Update
- Delete
- Query

Folder

```
app/repositories/
```

Example

```
UserService

↓

UserRepository

↓

PostgreSQL
```

Repositories should never contain business logic.

---

## Layer 4 – Database Layer

Responsible for persistence.

Technology

```
PostgreSQL
```

Stores

- Users
- Chats
- Messages
- OAuth Tokens
- Integrations
- Settings

Future

- Files
- Memories
- Notifications

---

## Layer 5 – Event Layer

Responsible for asynchronous communication.

Technology

```
RabbitMQ
```

Responsibilities

- Publish Events
- Consume Events
- Retry Failed Events
- Dead Letter Queue

Folder

```
app/events/
```

---

## Layer 6 – Worker Layer

Handles background tasks.

Folder

```
app/workers/
```

Examples

- Email Sync
- Calendar Sync
- Notification Delivery
- Embedding Requests
- Memory Compression
- File Indexing

Workers should never expose HTTP endpoints.

---

# 4. Backend Modules

```
app/

├── api
├── auth
├── users
├── chat
├── integrations
├── services
├── repositories
├── events
├── workers
├── middleware
├── database
├── core
├── config
└── tests
```

Each module owns its models, services, repositories, and routes where appropriate.

---

# 5. Request Lifecycle

Every request follows the same pipeline.

```
Client

↓

FastAPI

↓

Logging Middleware

↓

Authentication Middleware

↓

Validation

↓

Router

↓

Service

↓

Repository

↓

Database

↓

Response
```

If an event is generated:

```
Service

↓

Publish Event

↓

RabbitMQ

↓

Worker

↓

Background Processing
```

---

# 6. Authentication Flow

```
Client

↓

POST /login

↓

Auth Router

↓

Auth Service

↓

Verify Password

↓

Generate JWT

↓

Generate Refresh Token

↓

Store Refresh Token

↓

Return Tokens
```

Protected requests

```
Request

↓

JWT Middleware

↓

Verify Token

↓

Load User

↓

Continue Request
```

---

# 7. Chat Flow

```
Client

↓

POST /chat/{id}/message

↓

Store Message

↓

Publish MessageReceived Event

↓

AI Service Processes Message

↓

Receive AI Response

↓

Store Assistant Message

↓

Stream Response
```

The backend does not generate responses itself.

---

# 8. Integration Flow

Example

Google Calendar

```
User

↓

Connect Google

↓

OAuth

↓

Receive Tokens

↓

Encrypt Tokens

↓

Store Database

↓

Publish IntegrationConnected Event

↓

Background Sync
```

Every integration follows the same lifecycle.

---

# 9. Folder Responsibilities

## api/

Contains

- REST endpoints
- Request validation
- Response models

---

## auth/

Contains

- JWT
- OAuth
- Password hashing
- Login
- Registration

---

## chat/

Contains

- Chat logic
- Message storage
- Chat management

---

## users/

Contains

- User profile
- Preferences
- Settings

---

## repositories/

Contains database access only.

Example

```
UserRepository

ChatRepository

MessageRepository
```

---

## services/

Contains business logic.

Example

```
AuthService

UserService

ChatService

IntegrationService
```

---

## middleware/

Contains

- Authentication
- Logging
- Rate Limiting
- Request IDs
- Exception Handling

---

## events/

Contains

- Event definitions
- Event publisher
- Event consumers
- RabbitMQ configuration

---

## workers/

Contains

Background jobs.

Example

```
Email Worker

Calendar Worker

Notification Worker
```

---

## integrations/

Contains providers.

```
gmail/

calendar/

slack/

jira/

github/
```

Each provider implements the same interface.

---

## database/

Contains

- SQLAlchemy Base
- Session Management
- Engine
- Models
- Migrations

---

## config/

Contains

```
Settings

Environment Variables

Constants
```

---

## core/

Contains shared utilities.

Examples

- Security helpers
- Encryption
- Common exceptions
- Response utilities
- Dependency providers

---

# 10. Dependency Injection

Every service is injected.

Example

```
Router

↓

ChatService

↓

ChatRepository

↓

Database Session
```

Avoid creating services manually inside other services.

Benefits

- Easier testing
- Lower coupling
- Better maintainability

---

# 11. Error Handling

All exceptions are centralized.

Example

```
ValidationError

↓

Global Exception Handler

↓

JSON Response
```

Example response

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid input."
  }
}
```

HTTP status codes should be consistent across the application.

---

# 12. Logging Strategy

Every request generates a Request ID.

Logged information:

- Timestamp
- Request ID
- Endpoint
- User ID (if authenticated)
- Status Code
- Duration
- Errors

Sensitive information such as passwords, tokens, and API keys must never be logged.

---

# 13. Configuration

Configuration is loaded from environment variables.

Examples

```
DATABASE_URL

REDIS_URL

JWT_SECRET

RABBITMQ_URL

OPENAI_API_KEY

GOOGLE_CLIENT_ID
```

Environment-specific settings should be isolated using configuration classes.

---

# 14. Testing Strategy

Three testing layers are required.

## Unit Tests

Test:

- Services
- Utilities
- Repositories

---

## Integration Tests

Test:

- Database
- Authentication
- APIs
- Events

---

## End-to-End Tests

Test complete user workflows.

Example

```
Register

↓

Login

↓

Create Chat

↓

Send Message

↓

Receive Response
```

---

# 15. Security Principles

The backend follows these rules:

- Passwords hashed with Argon2
- JWT authentication
- Refresh token rotation
- OAuth token encryption
- HTTPS only in production
- CORS restrictions
- SQL injection prevention via ORM
- Input validation with Pydantic
- Rate limiting
- Secure HTTP headers

---

# 16. Scalability

The backend is stateless.

Any instance should be able to serve any request.

Scaling strategy:

- Multiple FastAPI instances
- Shared PostgreSQL
- Shared Redis
- RabbitMQ Cluster
- Load Balancer
- Container orchestration (Kubernetes in future)

No user session data is stored in application memory.

---

# 17. Coding Standards

Every module must follow:

- Single Responsibility Principle
- Dependency Injection
- Repository Pattern
- Service Pattern
- Type Hints
- Docstrings
- Structured Logging
- Consistent API responses
- No business logic inside routers
- No SQL inside services

---

# 18. Definition of Done

The backend architecture is considered complete when:

- All modules follow the layered architecture.
- APIs contain no business logic.
- Services are independent of HTTP.
- Repositories handle all database operations.
- Events are published through RabbitMQ.
- Background tasks execute asynchronously.
- Authentication is fully implemented.
- OpenAPI documentation is generated automatically.
- All modules include unit and integration tests.
- The AI team can consume backend APIs without modifying backend code.

---

**End of Document**