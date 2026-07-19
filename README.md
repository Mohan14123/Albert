# Albert - AI Assistant Platform

**Albert** is a production-ready, modular AI assistant platform built with scalability, maintainability, and parallel development in mind. The architecture enforces a strict separation of concerns, enabling independent teams to build and scale the system without interfering with each other's work.

## 🌟 Vision & High-Level Architecture
Albert is structured around three completely isolated domains:
*   **Frontend (Presentation Layer):** React / Next.js application handling UI, streaming chat, and state management.
*   **Backend (Business & API Layer):** API Gateway, Authentication, Event Bus, and Integration Services.
*   **AI (Reasoning & Memory Layer):** AI Orchestrator, Prompt/Context Builder, Memory System (Working, Semantic, LTM), and Tool Execution.

The system embraces an **Event-Driven Architecture**, ensuring that communication between services (e.g., chat services, memory, integrations) happens asynchronously and robustly.

---

## 🛠 Core Design Principles
1.  **Plug-and-Play Modules:** Every integration (Gmail, Calendar, Slack, etc.) is a standalone plugin.
2.  **Server-side Encrypted Memory:** Memory is processed, compressed, and encrypted purely on the server. The client holds no state other than UI.
3.  **Strict Boundaries:** The Frontend *never* directly talks to the Database or AI layer; everything flows through the documented API Gateway.
4.  **Stateless Services:** Designed for horizontal scaling using stateless APIs and queue-based background workers.

---

## 🤝 Team Roles & Collaboration Rules

Albert is built for parallel development. To prevent merge conflicts and tight coupling, responsibilities are strictly divided:

### Developer 1 — Backend Lead
*   **Owns:** REST APIs, DB, Authentication, Event Bus, Integrations (Plugins).
*   **Boundaries:** Never implements Frontend or AI reasoning. Exposes internal services via well-documented API contracts and Events.

### Developer 2 — AI Lead
*   **Owns:** AI Orchestration, Prompt Engineering, Memory Systems, RAG, Planning.
*   **Boundaries:** Never touches DB schemas, Backend infrastructure, or Frontend. Defines Request/Response payloads for any Backend actions needed.

### Developer 3 — Frontend Lead
*   **Owns:** UI, Components, Pages, Accessibility, Responsive Layouts.
*   **Boundaries:** Never writes Backend or AI logic. Communicates exclusively via Backend APIs.

---

## 📂 Project Structure

```
Albert/
├── backend/                  # Backend APIs, Gateway, and Services
├── ai/                       # AI Orchestration, Memory, and Prompts
├── frontend/                 # UI components and React pages
├── shared/                   # Shared types, contracts, and interfaces
├── infrastructure/           # Event Bus, DB, Queue, and Cache setup
├── docs/                     # Comprehensive architecture and API documentation
├── scripts/                  # Utilities and setup scripts
├── docker/                   # Containerization and orchestration configs
└── tests/                    # Independent unit and integration tests
```

## 📜 Documentation
For a deeper dive into the system's design, refer to the provided architectural documents:
*   [Architecture Overview](architecture.md)
*   [Developer Guidelines & Prompts](promt.md)
*   [System Rules](rules.md)

## 📄 License
This project is licensed under the terms specified in the `LICENSE` file.
