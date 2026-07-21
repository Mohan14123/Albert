# 🤖 Alfred AI — Production-Grade AI Personal Assistant Platform

> **Alfred AI** is an event-driven, decoupled AI assistant platform built with **Next.js 16**, **FastAPI**, and **Groq LLM (Llama 3.3 70B)**. Designed for speed, privacy, and modular extensibility.

---

## 🚨 Problem

In today's digital workflow, users face severe **context fragmentation**:
* **App Switching Overhead**: Constantly jumping between Gmail, Google Calendar, search engines, and note-taking apps destroys focus.
* **Stateless Chatbots**: Standard AI chatbots lack long-term memory of user preferences and cannot take actions on external services.
* **Monolithic Bottlenecks**: Traditional monolithic AI apps suffer from high response latencies, tight coupling, and lack of real-time streaming infrastructure.

---

## 💡 Solution

**Alfred AI** resolves these issues by delivering a unified, autonomous digital assistant:
* ⚡ **Sub-Second Streaming**: Powered by Groq's hardware-accelerated Llama 3.3 70B engine via Server-Sent Events (SSE).
* 🧠 **Persistent Server Memory**: Remembers user context, preferences, and details across sessions.
* 🛠 **Plug-and-Play Tools**: Autonomous intent planning that executes tools for math, web search, email management, and calendar events.
* 🛡 **Production Security**: Strict domain isolation, JWT authentication, and Argon2id password hashing.

---

## 🏗 Architecture Overview

Alfred AI follows a strict **Decoupled 3-Tier Architecture**:

```
 ┌─────────────────────────────────────────────────────────┐
 │             Frontend (Presentation Layer)               │
 │           React 19 / Next.js 16 (Turbopack)             │
 └────────────────────────────┬────────────────────────────┘
                              │ REST / SSE Stream
 ┌────────────────────────────▼────────────────────────────┐
 │              Backend (API & Domain Layer)               │
 │    FastAPI Gateway • JWT Auth • Repositories • SQLite   │
 └────────────────────────────┬────────────────────────────┘
                              │ Event Bus / Direct Proxy
 ┌────────────────────────────▼────────────────────────────┐
 │             AI Service (Reasoning Layer)                │
 │    AI Orchestrator • Intent Planner • Tool Registry     │
 └────────────────────────────┬────────────────────────────┘
                              │ OpenAI-Compatible API
 ┌────────────────────────────▼────────────────────────────┐
 │              LLM Provider (Groq Cloud)                  │
 │           Llama 3.3 70B Versatile Model               │
 └─────────────────────────────────────────────────────────┘
```

---

## 🔄 AI Workflow

1. **User Request**: User sends a prompt via the UI (e.g., *"Summarize my recent unread emails"*).
2. **Intent Planning**: The `LLMIntentPlanner` analyzes the input against registered tool schemas.
3. **Tool Execution**: If a tool is needed (e.g., `email.get_unread_messages`), the `DefaultToolExecutor` executes it and retrieves structured JSON data.
4. **Context Assembly**: `DefaultContextBuilder` injects memory, user profile data, and tool execution outputs into the system prompt.
5. **Generation & SSE Streaming**: Groq LLM generates the response, streamed word-by-word back to the user interface in real time.

---

## ⚙️ Backend Architecture

Built using **Domain-Driven Design (DDD)** and clean layered architecture:

```
backend/app/
├── api/v1/         # Versioned REST controllers & SSE endpoints
├── core/           # Security (Argon2id, JWT), middleware, dependencies
├── database/       # SQLAlchemy models & async engine
├── events/         # RabbitMQ contracts & publisher
├── repositories/   # Abstract database access layer (User, Chat, Message, etc.)
└── services/       # Domain business logic (Auth, Chat, Message, Integration)
```

---

## 📡 Event System

Alfred AI utilizes an **Asynchronous Event-Driven Architecture**:
* **Domain Events**: `user.created`, `message.received`, `message.stored`, `auth.login`, `auth.refreshed`.
* **RabbitMQ Contract**: Events are published to durable exchanges (`assistant.exchange`).
* **Resilient Fallback**: In offline local development, publishers catch connection exceptions gracefully to ensure zero downtime.

---

## 🔌 Plugin & Tool System

Extensible plug-and-play architecture (`Tool` base class + `ToolRegistry`):

| Tool | Registry Name | Description |
|:---|:---|:---|
| 🧮 **Calculator** | `calculator.compute` | Safe mathematical expression evaluation |
| 🔍 **Web Search** | `search.web` | Real-time web search engine query |
| ✉️ **Gmail Read** | `email.get_unread_messages` | Fetches & summarizes unread inbox emails |
| 📤 **Gmail Send** | `gmail.send` | Composes & dispatches emails |
| 📅 **Calendar** | `calendar.get_events` | Retrieves Google Calendar events |

---

## 🌐 API Endpoints

### Authentication (`/api/v1/auth`)
* `POST /register` — Register new user account & auto-create settings.
* `POST /login` — Authenticate and receive JWT access + refresh tokens.
* `POST /refresh` — Rotate access token using valid refresh token.
* `GET /me` — Retrieve current authenticated user profile.

### Chat & Messaging (`/api/v1/chats`)
* `GET /chats` — List user conversations.
* `POST /chats` — Create a new conversation.
* `POST /chats/{chat_id}/messages` — Send user message.
* `GET /chats/{chat_id}/messages/stream` — SSE endpoint for real-time AI streaming.

---

## 🧠 Memory System

* **Working Memory**: In-memory context window management for active conversation sessions.
* **Semantic Memory**: Server-side storage for user preferences and facts.
* **Encrypted Storage**: Sensitive data remains encrypted on the server side.

---

## 📸 Screenshots

### Sign Up / Authentication Screen
![Authentication Screen](docs/images/auth_screenshot.png)

---

## 🎥 Demo Video & Walkthrough

* **Live Web App**: [http://localhost:3000](http://localhost:3000)
* **Backend OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **AI Service OpenAPI Docs**: [http://localhost:8001/docs](http://localhost:8001/docs)

---

## 🚀 Local Setup & Installation

### Prerequisites
* Python 3.9+
* Node.js 18+

### 1. Clone Repository
```bash
git clone -b final2 https://github.com/Mohan14123/Albert.git Albert-final2
cd Albert-final2
```

### 2. Environment Configuration
Create `.env` with your Groq API Key:
```env
DEFAULT_AI_PROVIDER=openai
OPENAI_API_KEY=your_groq_api_key_here
OPENAI_API_BASE=https://api.groq.com/openai/v1
OPENAI_DEFAULT_MODEL=llama-3.3-70b-versatile
DATABASE_URL=sqlite+aiosqlite:///./assistant.db
```

### 3. Setup Python Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
venv/bin/pip install eval_type_backport greenlet aiosqlite -r backend/requirements.txt
```

### 4. Initialize Database
```bash
PYTHONPATH=.:backend venv/bin/python3 -c "
import asyncio
from app.database.engine import engine
from app.database.base import Base
import app.database.models

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init())
"
```

### 5. Launch Services

**Terminal 1 — AI Service (Port 8001):**
```bash
PYTHONPATH=. venv/bin/uvicorn ai.main:app --host 0.0.0.0 --port 8001
```

**Terminal 2 — Backend API Gateway (Port 8000):**
```bash
PYTHONPATH=backend venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 3 — Frontend Web App (Port 3000):**
```bash
cd frontend && npm install && npm run dev
```

---

## 🐳 Deployment

### Docker Compose Deployment
```bash
docker-compose up --build -d
```
This spins up PostgreSQL, Redis, RabbitMQ, FastAPI backend, AI Orchestrator, and Next.js frontend containers.

---

## 🤖 Codex Usage

**OpenAI Codex** and AI pair-programming agents played a critical role in the architecting and development of Alfred AI:

1. **Phased Architecture Refactoring**:
   * **Phase 4**: Designed and implemented the repository pattern (`UserRepository`, `ChatRepository`, `MessageRepository`, `RefreshTokenRepository`).
   * **Phase 5**: Developed the domain service layer (`AuthService`, `UserService`, `ChatService`, `MessageService`) enforcing clean domain separation.
   * **Phase 6**: Built event contracts (`schemas.py`, `publisher.py`) and graceful offline fallback mechanisms.
2. **Commit Granularity**: Codex was utilized to automate atomic Conventional Commits for every newly created repository and service file.
3. **Cross-Version Python 3.9 Compatibility**: Assisted in backporting type annotations (`from __future__ import annotations`), dataclasses, and custom `StrEnum` shims.

---

## ⚡ GPT-5.6 / LLM Model Usage

* **Primary Model**: Groq-accelerated `llama-3.3-70b-versatile` serving as the core reasoning engine.
* **Prompt Engineering**: Custom system instruction templates enforcing strict persona adherence (*"You are Alfred, a helpful AI assistant"*).
* **Robust Intent Planning**: Multi-shot intent classification mapping user prompts directly to tool contracts.

---

## 🗺 Future Roadmap

- [ ] **Multi-Agent Delegation**: Subagent spawning for background web research and long-running analysis.
- [ ] **Real-Time Voice Interface**: Full duplex WebRTC voice streaming directly in the frontend UI.
- [ ] **RAG Vector Search**: Integration with pgvector & ChromaDB for deep document search across uploaded PDFs and documents.
- [ ] **Full OAuth Integrations**: One-click Google & Microsoft account linking for live email/calendar sync.

---

## 📜 License
Licensed under the MIT License.
