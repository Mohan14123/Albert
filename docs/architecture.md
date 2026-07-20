# Architecture.md

# AI Assistant Platform Architecture

Version: 1.1

---

# 1. Vision

The platform is designed as a **production-ready, modular AI assistant** capable of integrating with external applications while remaining scalable, maintainable, and easy for multiple developers to extend simultaneously.

The entire system follows a strict separation of responsibilities between:

- Backend
- AI
- Frontend

Each module is independently deployable and communicates only through well-defined interfaces.

---

# 2. High-Level Architecture

```text
                    ┌─────────────────────────┐
                    │        Frontend         │
                    │ React / Next.js         │
                    └──────────┬──────────────┘
                               │
                         HTTPS REST API
                               │
                ┌──────────────▼──────────────┐
                │        API Gateway          │
                │ Authentication (JWT)        │
                │ Rate Limiting              │
                │ Validation                 │
                └──────────────┬──────────────┘
                               │
             ┌─────────────────┼──────────────────┐
             │                 │                  │
             ▼                 ▼                  ▼
     Chat Service       Memory Service     Integration Service
             │                 │                  │
             └─────────────────┼──────────────────┘
                               │
                       RabbitMQ & Redis Pub/Sub
                               │
         ┌─────────────────────┼──────────────────────┐
         ▼                     ▼                      ▼
   AI Orchestrator     Background Workers      Notification Service
         │
         ▼
 Prompt Builder
         │
         ▼
 Context Builder
         │
         ▼
 Vector Memory Retrieval (pgvector)
         │
         ▼
 Tool Selection
         │
         ▼
 LLM (OpenAI API)
         │
         ▼
 Response Pipeline (SSE Streaming)
         │
         ▼
 Backend API
         │
         ▼
 Frontend Client
```

---

# 3. Core Design Principles

The system is built around:

- Event Driven Architecture (RabbitMQ, Redis)
- Plug-and-Play Modules
- Independent Microservices (Backend, AI Worker)
- Stateless APIs
- Server-side Encrypted Vector Memory (pgvector + Fernet AES)
- AI Orchestrator
- Modular Integrations
- Loose Coupling & High Cohesion

---

# 4. Layered Architecture

```
Presentation Layer
    Frontend

──────────────

API Layer
    API Gateway
    Authentication
    Validation

──────────────

Business Layer
    Chat Service
    Memory Service
    Integration Service
    Notification Service

──────────────

AI Layer
    AI Orchestrator
    Prompt Builder
    Context Builder
    Tool Selection
    Memory Compression
    RAG (Vector Store)
    Response Formatter

──────────────

Infrastructure Layer
    RabbitMQ (Task Queue / Async Events)
    Redis (SSE Pub/Sub / Caching)
    PostgreSQL w/ pgvector (Relational & Vector DB)
```

---

# 5. Frontend Architecture

Responsibilities

- Chat UI
- Chat History
- Streaming Responses via Server-Sent Events (SSE)
- Authentication Screens
- Theme & State Management

Frontend never accesses the database or AI directly. Everything goes through Backend APIs.

---

# 6. Backend Architecture

Backend is divided into services.

## API Gateway
Responsible for routing, authentication, authorization, and validation.

## Chat Service
Responsible for conversation lifecycle, chat persistence, streaming responses (SSE mapping), and session management.

## Memory Service
Responsible for long-term memory, compression, **AES encryption**, retrieval (via cosine distance similarity), and storage using PostgreSQL **pgvector**.

## Integration Service
Responsible for Gmail, Slack, Jira, GitHub, Notion, etc.

## Event Bus
Responsible for communication between services.
AI responses are streamed via Redis Pub/Sub. System events are broadcasted via RabbitMQ.

---

# 7. AI Architecture

The AI system is completely separated from Backend.

Backend sends: Request, Context, Memory, Tool permissions.
The AI returns: Response, Tool Requests, Memory Updates.

## AI Workflow

```
User Message → Safety Layer → Intent Detection → Context Builder → Memory Retrieval → Prompt Builder → Planning → Tool Selection → Execute Tools → LLM → SSE Stream → Memory Compression
```

---

# 8. Memory Architecture

Memory is stored only on the server, encrypted at rest via Fernet AES, and embedded using `text-embedding-3-small`. Retrieval uses pgvector's cosine distance query.

---

# 9. AI Orchestrator

Responsible for coordinating AI modules, maintaining context window token limits, executing plugins, and streaming partial chunks via Redis Pub/Sub.

---

# 10. Plugin Architecture

Every integration follows a standard Tool interface. Each plugin is independently deployable and mockable.

---

# 11. Event Driven Architecture

No module depends directly on another module. We use events like:
`message.received`, `message.stored`, `chat.created`

---

# 12. Security Architecture

Authentication uses JWT.
Stored memories are symmetrically encrypted using AES-256 (Fernet) in the database.
Secrets are managed by environment variables.

---

# 13. Database Architecture

Primary Database (PostgreSQL):
- Users, Chats, Messages, Metadata
- Memory Storage (Vector Embeddings via pgvector, Encrypted Content)

Cache (Redis):
- Pub/Sub for SSE streaming
- Temporary AI Context Window State

---

# 14. Scalability Strategy

The architecture supports horizontal scaling:
- Services remain stateless.
- Workers process asynchronous tasks independently.
- Memory storage scales via relational indexing and pgvector HNSW indices.
