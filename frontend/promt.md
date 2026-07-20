# Project Prompt

## Objective

You are contributing to a shared AI Assistant project.

There are **three developers working independently in parallel**.

Each developer owns a separate part of the system.

Your responsibility is to complete only the work assigned to your role while preserving the overall architecture.

---

# Team Structure

Developer 1 — Backend Lead

Responsible for:

- REST APIs
- Authentication
- Database
- Event Bus
- Infrastructure
- Integrations
- Security
- Plugin System
- Storage
- API Contracts

Must NOT implement:

- Frontend
- AI reasoning
- Prompt engineering

---

Developer 2 — AI Lead

Responsible for:

- AI Orchestration
- Memory System
- Prompt Engineering
- Context Management
- Compression
- RAG
- AI Workflows
- Planning
- Tool Selection

Must NOT implement:

- Backend infrastructure
- Database schemas
- Frontend

If backend functionality is required, define only:

- Required Endpoint
- Required Event
- Request Payload
- Response Payload

---

Developer 3 — Frontend Lead

Responsible for:

- UI
- Components
- Pages
- Accessibility
- UX
- Responsive Layouts
- State Management

Must NOT implement:

- Backend logic
- AI logic
- Database logic
- Authentication internals

Frontend communicates only through backend APIs.

---

# Existing Architecture

The following architecture is FINAL.

Do NOT redesign it.

- Event Driven Architecture
- Plug-and-Play Modules
- Server-side Encrypted Memory
- AI Orchestrator
- Modular Services
- REST APIs
- Versioned APIs
- Queue-based Processing
- Independent Services

Only extend the architecture.

Never replace it.

---

# Collaboration Rules

Assume all three developers are actively working simultaneously.

Before changing anything ask:

- Is this my responsibility?
- Does this belong to another developer?
- Can I expose an interface instead?

If another developer's work is required:

Define ONLY:

- API
- Event
- Contract
- Interface

Never implement another developer's module.

---

# Deliverables

Every implementation must include:

- Documentation
- Folder Structure
- API Documentation (if applicable)
- Examples
- Walkthrough
- Error Handling
- Future Extension Notes

---

# Documentation Structure

Every major module must include documentation inside:

docs/

API contracts should be stored inside:

api/

---

# Coding Principles

Prioritize:

- Scalability
- Maintainability
- Loose Coupling
- High Cohesion
- Plug-and-Play
- Event Driven Communication
- Stateless Services
- Clear Interfaces

Avoid:

- Tight coupling
- Hidden dependencies
- Hardcoded services
- Shared mutable state

---

# Goal

Build one unified production-quality system while allowing three developers to work independently without interfering with each other's work.