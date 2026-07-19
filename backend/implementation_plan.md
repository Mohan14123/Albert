# Albert Backend — Implementation Plan (Final)

> **Role:** Developer 1 — Backend Lead  
> **Scope:** All changes are confined to `backend/` only. No files outside `backend/` will be created, modified, or deleted.  
> **Architecture:** FastAPI · PostgreSQL · Redis · RabbitMQ · SQLAlchemy · Alembic · Celery · Pytest  
> **Date:** 18 July 2026

---

## Guiding Constraints

- **No changes outside `backend/`.** The AI Lead owns `ai/` and the Frontend Lead owns `frontend/`.
- **Never redesign** the Event Bus, Database Models, Folder Structure, or API Contracts. Only **extend** them.
- **No AI reasoning or prompt engineering** — that belongs to Developer 2.
- **No Frontend UI logic** — that belongs to Developer 3.
- Where the AI or Frontend needs something from the backend, we expose **documented API contracts and Events only**.

---

## Resolved Decisions

| # | Question | Decision |
|---|----------|----------|
| 1 | **AI Communication Protocol** | RabbitMQ events as primary (async, scalable). REST endpoints (`/internal/ai/respond`, `/internal/ai/callback`) available as alternative for the AI team to call back. |
| 2 | **OAuth Providers** | Build base interface + registry first. Implement Google (Gmail + Calendar) fully. Stub Slack, GitHub, Jira — implement them at the very end. |
| 3 | **Redis Dependency** | Prioritize Docker Compose setup in Phase 1 so all infrastructure (PostgreSQL, Redis, RabbitMQ) is available from the start. |

---

## Current State

The `backend/` directory currently contains only:
- `.gitignore`
- `docs/` (10 comprehensive design documents)
- `progress.md` (empty)

**Zero application code exists.** The entire backend is built from scratch following the architecture defined in the docs.

---

## Phase 1 — Project Scaffolding, Configuration & Docker

Set up the Python project, configuration system, and **all infrastructure via Docker Compose** so every subsequent phase has databases and queues ready.

### New Files

#### `backend/requirements.txt`
- FastAPI, Uvicorn[standard], Pydantic, pydantic-settings
- SQLAlchemy 2.0, Alembic, psycopg[binary] (async PostgreSQL driver)
- redis[hiredis], aio-pika (RabbitMQ async client), celery
- argon2-cffi (password hashing), python-jose[cryptography] (JWT), cryptography (AES-256)
- httpx (async HTTP client for AI service communication)
- pytest, pytest-asyncio, pytest-cov, httpx (test client)
- ruff, black, mypy

#### `backend/pyproject.toml`
- Black (line-length=88), Ruff rules, MyPy strict config

#### `backend/.env.example`
- All keys from Environment.md §24 (APP_NAME, DATABASE_URL, REDIS_URL, RABBITMQ_URL, JWT_SECRET, OAuth vars, AI_SERVICE_URL, CORS_ORIGINS, rate limits, feature flags)

#### `backend/app/__init__.py`
- Empty package init

#### `backend/app/config/__init__.py`
- Empty package init

#### `backend/app/config/settings.py`
- Pydantic `BaseSettings` class loading every env var from Environment.md
- Startup validation: fail-fast if required vars are missing or invalid
- Environment enum: `local | development | staging | production`
- DB pool settings, JWT expiry settings, rate limit settings all centralized here

#### `backend/docker/docker-compose.yml`
- **PostgreSQL 16** — port 5432, healthcheck, named volume
- **Redis 7** — port 6379, healthcheck
- **RabbitMQ 3.13** — ports 5672 (AMQP) + 15672 (management dashboard), healthcheck
- **PgAdmin** (optional, dev only) — port 5050

#### `backend/docker/docker-compose.prod.yml`
- Production overrides: no PgAdmin, resource limits, restart policies

#### `backend/docker/.env.example`
- Docker-specific env vars (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, RABBITMQ_DEFAULT_USER, etc.)

### Deliverables
- `docker compose up -d` starts PostgreSQL, Redis, RabbitMQ
- `pip install -r requirements.txt` installs all dependencies
- Settings class validates environment on import

---

## Phase 2 — Database Layer (PostgreSQL + SQLAlchemy + Alembic)

Implement the full database layer as specified in Database.md.

### New Files

#### `backend/app/database/__init__.py`

#### `backend/app/database/engine.py`
- Async SQLAlchemy engine (`create_async_engine`)
- Async session factory (`async_sessionmaker`)
- Connection pooling: `pool_size` and `max_overflow` from settings
- `get_db_session` async generator for FastAPI dependency injection

#### `backend/app/database/base.py`
- `Base` declarative base with:
  - `id`: UUID (v4), primary key, server-default
  - `created_at`: TIMESTAMP with timezone, server-default `now()`
  - `updated_at`: TIMESTAMP with timezone, `onupdate=now()`
  - Optional `deleted_at`: TIMESTAMP (soft delete support)

#### `backend/app/database/models/__init__.py`
- Re-exports all models for Alembic autodiscovery

#### `backend/app/database/models/user.py`
- **Table: `users`**
- Columns: email (VARCHAR 255, UNIQUE), password_hash (TEXT), full_name (VARCHAR 100), assistant_name (VARCHAR 50, default "Albert"), timezone (VARCHAR 50), language (VARCHAR 20), is_active (BOOLEAN, default True)
- Relationships: chats, refresh_tokens, settings, integrations

#### `backend/app/database/models/refresh_token.py`
- **Table: `refresh_tokens`**
- Columns: user_id (UUID FK → users.id, CASCADE), token_hash (TEXT), expires_at (TIMESTAMP), revoked (BOOLEAN, default False)

#### `backend/app/database/models/chat.py`
- **Table: `chats`**
- Columns: user_id (UUID FK → users.id, CASCADE), title (VARCHAR 255), archived (BOOLEAN, default False)
- Relationships: messages

#### `backend/app/database/models/message.py`
- **Table: `messages`**
- Columns: chat_id (UUID FK → chats.id, CASCADE), role (ENUM: user/assistant/system), content (TEXT), status (ENUM: pending/completed/failed), token_count (INTEGER, nullable)
- Indexes: (chat_id, created_at) composite

#### `backend/app/database/models/user_settings.py`
- **Table: `user_settings`**
- Columns: user_id (UUID FK → users.id, CASCADE, UNIQUE — one-to-one), theme (VARCHAR), language (VARCHAR), notifications (BOOLEAN, default True)

#### `backend/app/database/models/integration.py`
- **Table: `integrations`**
- Columns: user_id (UUID FK → users.id, CASCADE), provider (VARCHAR), status (ENUM: connected/expired/disconnected), connected_at (TIMESTAMP), last_sync (TIMESTAMP, nullable)
- Indexes: (user_id, provider) composite unique

#### `backend/app/database/models/oauth_token.py`
- **Table: `oauth_tokens`**
- Columns: integration_id (UUID FK → integrations.id, CASCADE), access_token (TEXT — AES-256 encrypted), refresh_token (TEXT — AES-256 encrypted), expires_at (TIMESTAMP)

#### `backend/alembic.ini`
- Points to `backend/alembic/` directory
- Uses `DATABASE_URL` from environment

#### `backend/alembic/env.py` + `backend/alembic/versions/001_initial_schema.py`
- Auto-generates migration from all models
- Creates all 7 tables, all indexes (users.email, messages.chat_id, messages.created_at, refresh_tokens.user_id, integrations.user_id, oauth_tokens.integration_id, chats.user_id), composite indexes, foreign keys, cascading rules

### Deliverables
- `alembic upgrade head` creates the full schema
- All relationships, constraints, indexes match Database.md exactly

---

## Phase 3 — Core Utilities & Middleware

Shared utilities and the middleware stack from Backend-Architecture.md §9-12.

### New Files

#### `backend/app/core/__init__.py`

#### `backend/app/core/security.py`
- **Password hashing:** Argon2id (hash, verify) via `argon2-cffi`
- **Token encryption:** AES-256-GCM encrypt/decrypt for OAuth tokens via `cryptography`
- **JWT:** Create access token (15 min), create refresh token (random 64 bytes), verify/decode JWT via `python-jose`

#### `backend/app/core/exceptions.py`
- Exception hierarchy:
  - `AuthenticationError` → 401
  - `AuthorizationError` → 403
  - `ValidationError` → 422
  - `NotFoundError` → 404
  - `ConflictError` → 409
  - `ProviderError` → 502
  - `RateLimitedError` → 429

#### `backend/app/core/responses.py`
- `success_response(data)` → `{"success": true, "data": {...}}`
- `error_response(code, message)` → `{"success": false, "error": {"code": "...", "message": "..."}}`
- `paginated_response(data, page, limit, total)` → includes `pagination` object

#### `backend/app/core/dependencies.py`
- FastAPI `Depends` providers:
  - `get_db` → yields async DB session
  - `get_current_user` → extracts + verifies JWT, loads user
  - `get_settings` → returns cached settings singleton
  - `require_role(role)` → RBAC check

#### `backend/app/middleware/__init__.py`

#### `backend/app/middleware/logging_middleware.py`
- Generates `X-Request-ID` (UUID) per request
- Structured JSON logs: timestamp, request_id, method, path, user_id, status_code, duration_ms
- Sensitive fields (password, token, secret) are never logged

#### `backend/app/middleware/authentication.py`
- Extracts `Authorization: Bearer <token>` header
- Verifies JWT signature + expiration
- Loads user from DB, attaches to request state
- Skips public routes (login, register, refresh, health)

#### `backend/app/middleware/rate_limiting.py`
- Redis-backed sliding window rate limiter
- Per-IP limits for auth endpoints: Login 5/min, Register 3/min
- Per-user limits for protected endpoints: Chat 60/min, Messages 120/min, Integrations 10/min

#### `backend/app/middleware/exception_handler.py`
- Global handler catching all custom exceptions → standard JSON error responses
- Catches unhandled exceptions → 500 with `INTERNAL_ERROR` code
- Stack traces logged server-side only, never exposed to client

#### `backend/app/middleware/security_headers.py`
- Adds to every response:
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Content-Security-Policy: default-src 'self'`
  - `Referrer-Policy: strict-origin-when-cross-origin`

### Deliverables
- All security functions unit-testable in isolation
- Middleware stack composable and order-independent

---

## Phase 4 — Repository Layer

Pure data-access layer. No business logic. All async.

### New Files

#### `backend/app/repositories/__init__.py`

#### `backend/app/repositories/user_repository.py`
- `create(user_data)`, `get_by_id(user_id)`, `get_by_email(email)`, `update(user_id, data)`, `soft_delete(user_id)`

#### `backend/app/repositories/refresh_token_repository.py`
- `create(user_id, token_hash, expires_at)`, `get_by_hash(hash)`, `revoke(token_id)`, `revoke_all_for_user(user_id)`

#### `backend/app/repositories/chat_repository.py`
- `create(user_id, title)`, `get_by_id(chat_id)`, `get_by_user(user_id, page, limit)`, `update(chat_id, data)`, `archive(chat_id)`, `soft_delete(chat_id)`

#### `backend/app/repositories/message_repository.py`
- `create(chat_id, role, content, status)`, `get_by_chat(chat_id, page, limit)`, `update_status(message_id, status)`

#### `backend/app/repositories/user_settings_repository.py`
- `create(user_id, defaults)`, `get_by_user(user_id)`, `update(user_id, data)`

#### `backend/app/repositories/integration_repository.py`
- `create(user_id, provider)`, `get_by_user(user_id)`, `get_by_user_and_provider(user_id, provider)`, `update_status(id, status)`, `update_last_sync(id)`, `delete(id)`

#### `backend/app/repositories/oauth_token_repository.py`
- `create(integration_id, encrypted_access, encrypted_refresh, expires_at)`, `get_by_integration(integration_id)`, `update(id, data)`, `delete(id)`

### Deliverables
- Every repository method uses the async session
- All queries use parameterized statements (SQLAlchemy ORM)
- Pagination returns `(items, total_count)`

---

## Phase 5 — Service Layer

All business logic. Services are injected via FastAPI `Depends` and never touch HTTP directly.

### New Files

#### `backend/app/services/__init__.py`

#### `backend/app/services/auth_service.py`
- `register(email, password, full_name)`:
  - Check duplicate email → hash password → create user → create default settings → publish `UserCreated` event → return user_id
- `login(email, password)`:
  - Verify credentials → check lockout (Redis, 5 attempts → 15 min) → generate JWT (15 min) + refresh token → hash refresh → store in DB → publish `UserLoggedIn` → return tokens
- `refresh(refresh_token)`:
  - Validate token hash → check not revoked/expired → generate new JWT + new refresh token → revoke old → store new → publish `TokenRefreshed`
- `logout(refresh_token)`:
  - Revoke token → publish `UserLoggedOut`
- `logout_all(user_id)`:
  - Revoke all refresh tokens for user

#### `backend/app/services/user_service.py`
- `get_profile(user_id)`, `update_profile(user_id, data)`, `get_settings(user_id)`, `update_settings(user_id, data)`

#### `backend/app/services/chat_service.py`
- `create_chat(user_id, title)` → create in DB → publish `ChatCreated` → return chat_id
- `get_chats(user_id, page, limit)` → paginated list
- `get_chat(user_id, chat_id)` → single chat with ownership check
- `rename_chat(user_id, chat_id, title)` → ownership check → update
- `delete_chat(user_id, chat_id)` → soft delete → publish `ChatDeleted`

#### `backend/app/services/message_service.py`
- `send_message(user_id, chat_id, content)`:
  - Verify chat ownership → store user message (status: pending) → publish `MessageReceived` event (RabbitMQ — AI Worker consumes this) → return message_id + status:processing
- `get_messages(user_id, chat_id, page, limit)` → paginated, ordered by created_at
- `store_ai_response(chat_id, content, token_count)`:
  - Store assistant message (status: completed) → publish `MessageStored`
  - Called by the AI callback endpoint

#### `backend/app/services/integration_service.py`
- `get_integrations(user_id)` → list all connected integrations
- `connect(user_id, provider)` → generate OAuth redirect URL via provider config → return URL
- `handle_callback(provider, code, state)` → exchange auth code → encrypt tokens (AES-256) → store → publish `IntegrationConnected`
- `disconnect(user_id, provider)` → delete tokens → update status → publish `IntegrationDisconnected`
- `trigger_sync(user_id, provider)` → publish `IntegrationSynced` event for background worker
- `get_status(user_id, provider)` → return integration status + last_sync

### Deliverables
- Every service method is transactional (commit only on success, rollback on failure)
- Events published only after successful DB commit (outbox-safe)
- All services testable with mocked repositories

---

## Phase 6 — Event Bus (RabbitMQ)

The event-driven backbone as defined in Events.md. **Primary communication path for AI.**

### New Files

#### `backend/app/events/__init__.py`

#### `backend/app/events/schemas.py`
- `DomainEvent` dataclass:
  - `event_id` (UUID), `event_name` (str), `version` ("1.0"), `timestamp` (UTC ISO), `producer` (str), `correlation_id` (UUID), `payload` (dict)
- `to_json()` / `from_json()` serialization

#### `backend/app/events/exchanges.py`
- Constants: `DOMAIN_EXCHANGE = "domain.exchange"`, `INTEGRATION_EXCHANGE = "integration.exchange"`, `NOTIFICATION_EXCHANGE = "notification.exchange"`, `SYSTEM_EXCHANGE = "system.exchange"`
- Exchange type: `topic`

#### `backend/app/events/routing.py`
- Routing key constants:
  - `USER_CREATED = "user.created"`, `USER_UPDATED = "user.updated"`
  - `CHAT_CREATED = "chat.created"`, `CHAT_DELETED = "chat.deleted"`
  - `MESSAGE_RECEIVED = "message.received"`, `MESSAGE_STORED = "message.stored"`, `MESSAGE_FAILED = "message.failed"`
  - `AI_RESPONSE_GENERATED = "message.generated"`
  - `INTEGRATION_CONNECTED = "integration.connected"`, `INTEGRATION_DISCONNECTED = "integration.disconnected"`, `INTEGRATION_SYNCED = "integration.synced"`, `INTEGRATION_EXPIRED = "integration.expired"`
  - `USER_LOGGED_IN = "auth.login"`, `USER_LOGGED_OUT = "auth.logout"`, `TOKEN_REFRESHED = "auth.refreshed"`, `PASSWORD_CHANGED = "auth.password_changed"`

#### `backend/app/events/publisher.py`
- `EventPublisher` class:
  - Connects to RabbitMQ via `aio-pika`
  - `publish(exchange, routing_key, event: DomainEvent)` → serialize to JSON → publish with correlation_id
  - Structured logging on every publish (event_id, routing_key, duration)
  - Connection pooling and auto-reconnect

#### `backend/app/events/consumer.py`
- `BaseConsumer` class:
  - Connects to queue, binds to exchange + routing key
  - Acknowledgement after successful processing
  - Idempotency: tracks processed `event_id` set (Redis-backed)
  - Retry: 3 attempts with exponential backoff → Dead Letter Queue on final failure
  - `on_message(event: DomainEvent)` — abstract method for subclasses

#### `backend/app/events/handlers/__init__.py`

#### `backend/app/events/handlers/chat.py`
- Handles `AI_RESPONSE_GENERATED` → calls `message_service.store_ai_response()`

#### `backend/app/events/handlers/auth.py`
- Handles auth events → audit logging

#### `backend/app/events/handlers/integration.py`
- Handles `INTEGRATION_CONNECTED` → triggers initial sync

#### `backend/app/events/handlers/notification.py`
- Handles `USER_CREATED`, `INTEGRATION_CONNECTED` → placeholder for notification delivery

### Deliverables
- `EventPublisher` usable by all services via DI
- Queue naming convention: `<domain>.<consumer>.queue` (e.g., `chat.ai.queue`)
- DLQ per exchange: `message.dlq`, `integration.dlq`, `notification.dlq`
- All events follow the standard schema with correlation IDs for end-to-end tracing

---

## Phase 7 — API Layer (FastAPI Routers)

REST endpoints as specified in API.md. **Routers contain zero business logic** — they validate input, call services, and format output.

### New Files

#### `backend/app/main.py`
- FastAPI app initialization with metadata (title, version, description)
- Middleware registration order: SecurityHeaders → Logging → Authentication → RateLimiting → ExceptionHandler
- Router inclusion under `/api/v1/` prefix
- Startup hooks: initialize DB engine, connect RabbitMQ, connect Redis
- Shutdown hooks: close DB pool, close RabbitMQ, close Redis
- CORS middleware from settings (`CORS_ORIGINS`)
- OpenAPI / Swagger auto-generated at `/docs` and `/openapi.json`

#### `backend/app/api/__init__.py`

#### `backend/app/api/v1/__init__.py`

#### `backend/app/api/v1/auth.py`
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | Public | Register new user |
| POST | `/api/v1/auth/login` | Public | Login, returns JWT + refresh |
| POST | `/api/v1/auth/refresh` | Public | Rotate tokens |
| POST | `/api/v1/auth/logout` | Protected | Revoke refresh token |
| POST | `/api/v1/auth/logout-all` | Protected | Revoke all sessions |
| GET | `/api/v1/auth/me` | Protected | Get current user |

#### `backend/app/api/v1/users.py`
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/v1/users/me` | Protected |
| PATCH | `/api/v1/users/me` | Protected |
| GET | `/api/v1/users/settings` | Protected |
| PATCH | `/api/v1/users/settings` | Protected |

#### `backend/app/api/v1/chats.py`
| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/v1/chats` | Protected |
| GET | `/api/v1/chats` | Protected (paginated) |
| GET | `/api/v1/chats/{chat_id}` | Protected |
| PATCH | `/api/v1/chats/{chat_id}` | Protected |
| DELETE | `/api/v1/chats/{chat_id}` | Protected (soft delete) |

#### `backend/app/api/v1/messages.py`
| Method | Endpoint | Auth | Notes |
|--------|----------|------|-------|
| POST | `/api/v1/chats/{chat_id}/messages` | Protected | Publishes `MessageReceived` event |
| GET | `/api/v1/chats/{chat_id}/messages` | Protected | Paginated |
| GET | `/api/v1/chats/{chat_id}/stream` | Protected | SSE (`text/event-stream`) |

#### `backend/app/api/v1/integrations.py`
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/v1/integrations` | Protected |
| POST | `/api/v1/integrations/{provider}/connect` | Protected |
| GET | `/api/v1/integrations/{provider}/callback` | Public (OAuth redirect) |
| DELETE | `/api/v1/integrations/{provider}` | Protected |
| POST | `/api/v1/integrations/{provider}/sync` | Protected |
| GET | `/api/v1/integrations/{provider}/status` | Protected |

#### `backend/app/api/v1/health.py`
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/health` | Public | `{"status": "healthy"}` |
| GET | `/api/v1/ready` | Public | Checks DB + Redis + RabbitMQ |
| GET | `/api/v1/version` | Public | Returns app version |

#### `backend/app/api/internal/__init__.py`

#### `backend/app/api/internal/ai.py`
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/internal/ai/respond` | Internal (API key) | Backend → AI service request |
| POST | `/internal/ai/callback` | Internal (API key) | AI → Backend response callback |

#### `backend/app/api/webhooks/__init__.py`

#### `backend/app/api/webhooks/providers.py`
| Method | Endpoint | Notes |
|--------|----------|-------|
| POST | `/webhooks/gmail` | Verify signature → publish event → return 200 |
| POST | `/webhooks/calendar` | Same pattern |
| POST | `/webhooks/slack` | Same pattern |
| POST | `/webhooks/jira` | Same pattern |

#### Pydantic Request/Response Schemas

#### `backend/app/api/schemas/__init__.py`

#### `backend/app/api/schemas/auth.py`
- `RegisterRequest`, `LoginRequest`, `RefreshRequest`, `TokenResponse`, `UserResponse`

#### `backend/app/api/schemas/users.py`
- `ProfileUpdateRequest`, `SettingsUpdateRequest`, `ProfileResponse`, `SettingsResponse`

#### `backend/app/api/schemas/chats.py`
- `CreateChatRequest`, `RenameChatRequest`, `ChatResponse`, `ChatListResponse`

#### `backend/app/api/schemas/messages.py`
- `SendMessageRequest`, `MessageResponse`, `MessageListResponse`

#### `backend/app/api/schemas/integrations.py`
- `ConnectResponse`, `IntegrationResponse`, `IntegrationStatusResponse`

### Deliverables
- All endpoints return standard `{"success": true/false, ...}` format
- Pagination on all list endpoints: `?page=1&limit=20`
- SSE streaming endpoint for real-time AI responses
- Automatic OpenAPI documentation

---

## Phase 8 — Integration Providers, Workers, Docker & Testing

Background workers, the Google integration, containerization, and test suite.

### Integration Providers

#### `backend/app/integrations/__init__.py`

#### `backend/app/integrations/base.py`
- Abstract `BaseIntegration` class defining the interface:
  - `connect()`, `disconnect()`, `refresh_token()`, `sync()`, `webhook()`, `health_check()`

#### `backend/app/integrations/registry.py`
- Provider registry dict: `{"gmail": GmailIntegration, "calendar": CalendarIntegration, ...}`
- `get_provider(name)` → returns integration instance

#### `backend/app/integrations/manager.py`
- `IntegrationManager`: delegates to registry, handles token refresh/encryption

#### `backend/app/integrations/exceptions.py`
- `TokenExpired`, `ProviderUnavailable`, `InvalidOAuthCode`, `WebhookVerificationFailed`

#### `backend/app/integrations/oauth.py`
- Shared OAuth helpers: build redirect URL, exchange code, refresh token

#### `backend/app/integrations/schemas.py`
- Provider config schema: client_id, client_secret, scopes, redirect_uri, api_base_url

#### `backend/app/integrations/gmail/` (Full Implementation)
- `service.py` — GmailIntegration implementing BaseIntegration
- `oauth.py` — Google OAuth specifics (scopes: gmail.readonly, userinfo.email, openid)
- `sync.py` — Background email sync logic
- `webhook.py` — Gmail push notification handler

#### `backend/app/integrations/calendar/` (Full Implementation)
- `service.py` — CalendarIntegration
- `oauth.py` — Google Calendar OAuth (scopes: calendar.readonly)
- `sync.py` — Event sync logic

#### `backend/app/integrations/slack/` (Stub)
- `service.py` — Stub implementing BaseIntegration, raises `NotImplementedError`

#### `backend/app/integrations/github/` (Stub)
- `service.py` — Stub

#### `backend/app/integrations/jira/` (Stub)
- `service.py` — Stub

### Workers

#### `backend/app/workers/__init__.py`

#### `backend/app/workers/ai_worker.py`
- Consumes `MessageReceived` from `chat.ai.queue`
- Forwards message context to AI service URL (`AI_SERVICE_URL`) via httpx
- On AI response → publishes `AIResponseGenerated`

#### `backend/app/workers/sync_worker.py`
- Consumes `IntegrationSynced` from `integration.sync.queue`
- Calls provider's `sync()` method
- On completion → publishes sync status event

#### `backend/app/workers/notification_worker.py`
- Consumes `IntegrationConnected`, `UserCreated`
- Placeholder for push/email notification delivery

### Docker

#### `backend/docker/backend.Dockerfile`
- Python 3.12 slim, multi-stage build
- Stage 1: install dependencies
- Stage 2: copy app code, run with uvicorn

#### `backend/docker/worker.Dockerfile`
- Same base, runs celery worker instead of uvicorn

#### `backend/docker/nginx.conf`
- Reverse proxy to backend:8000
- Security headers
- HTTPS termination ready
- Gzip compression

### Testing

#### `backend/tests/__init__.py`

#### `backend/tests/conftest.py`
- Test database (SQLite in-memory or test PostgreSQL)
- Async test client via httpx
- Fixtures: test_user, test_chat, auth_headers, db_session

#### `backend/tests/test_auth.py`
- Register → Login → Use token → Refresh → Logout → Logout-all
- Failed login lockout (6th attempt returns 429)
- Invalid credentials return 401

#### `backend/tests/test_chat.py`
- Create → List (pagination) → Get → Rename → Delete (soft)
- Ownership checks (user A can't access user B's chats)

#### `backend/tests/test_messages.py`
- Send message → verify event published → list messages (paginated, ordered)
- SSE stream endpoint returns `text/event-stream`

#### `backend/tests/test_integrations.py`
- Connect Google → verify OAuth redirect URL
- Disconnect → verify status change
- Stub providers raise appropriate errors

#### `backend/tests/test_health.py`
- `/health` returns 200 + `{"status": "healthy"}`
- `/ready` checks all infrastructure
- `/version` returns correct version string

### Scripts

#### `backend/scripts/seed.py`
- Creates a test user (email: `test@albert.dev`, password: `TestPassword@123`)
- Creates 3 sample chats with messages

#### `backend/scripts/generate_secret.py`
- Generates a cryptographically secure 256-bit key for JWT_SECRET and TOKEN_ENCRYPTION_KEY

---

## Verification Plan

### Automated Tests
```bash
# From backend/ directory
pytest tests/ -v --cov=app --cov-report=term-missing

# Lint + format + type check
ruff check app/
black --check app/
mypy app/
```

### Manual Verification
1. `cd backend/docker && docker compose up -d` → all services healthy
2. `alembic upgrade head` → schema created
3. `uvicorn app.main:app --reload` → server starts
4. `GET /api/v1/health` → `{"status": "healthy"}`
5. `GET /api/v1/ready` → DB + Redis + RabbitMQ all pass
6. Register → Login → Create chat → Send message → Verify `MessageReceived` event in RabbitMQ dashboard (localhost:15672)
7. OpenAPI docs at `/docs` show all endpoints

---

## File Summary

| Phase | New Files | Directory |
|-------|-----------|-----------|
| 1 — Scaffolding & Docker | ~8 | `backend/`, `backend/app/config/`, `backend/docker/` |
| 2 — Database | ~13 | `backend/app/database/`, `backend/alembic/` |
| 3 — Core & Middleware | ~10 | `backend/app/core/`, `backend/app/middleware/` |
| 4 — Repositories | ~8 | `backend/app/repositories/` |
| 5 — Services | ~6 | `backend/app/services/` |
| 6 — Event Bus | ~9 | `backend/app/events/` |
| 7 — API Routers | ~18 | `backend/app/api/`, `backend/app/main.py` |
| 8 — Integrations/Workers/Docker/Tests | ~25 | `backend/app/integrations/`, `backend/app/workers/`, `backend/docker/`, `backend/tests/`, `backend/scripts/` |
| **Total** | **~97** | **`backend/` only** |

> **Every single file lives strictly under `backend/`.** No files in `ai/`, `frontend/`, or the project root are created or modified.

---

**Status: APPROVED — Ready for execution.**
