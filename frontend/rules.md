# Project Rules

These rules are mandatory.

Failure to follow them will create merge conflicts and inconsistent architecture.

---

# Rule 1

Three developers are working independently.

Always assume someone else is modifying another part of the project.

Never edit another developer's files.

---

# Rule 2

No merge conflicts should occur.

To achieve this:

- Never rename shared folders.
- Never move existing files.
- Never delete files created by another developer.
- Never modify another developer's APIs.
- Never change another developer's documentation.
- Never modify another developer's configuration.

Only add your own work.

---

# Rule 3

Respect ownership.

Backend owns:

backend/

AI owns:

ai/

Frontend owns:

frontend/

Do not modify folders outside your ownership unless explicitly instructed.

---

# Rule 4

Communication between modules must happen only through interfaces.

Examples:

Backend

- REST API
- Events

AI

- API Contracts
- Event Contracts

Frontend

- REST APIs

Never access another module directly.

---

# Rule 5

Never redesign the architecture.

Do not replace:

- Event Bus
- AI Orchestrator
- Memory System
- API Contracts
- Database Models
- Folder Structure

Only extend them.

---

# Rule 6

Every new component must be Plug-and-Play.

A component should be removable without affecting the rest of the application.

---

# Rule 7

Keep services loosely coupled.

Avoid:

- Circular dependencies
- Shared business logic
- Direct database access across modules
- Hardcoded integrations

---

# Rule 8

All public interfaces must be documented.

Every API

Every Event

Every Payload

Every Response

must have documentation.

---

# Rule 9

Never duplicate functionality.

If another module already provides a feature:

Use its interface.

Do not recreate it.

---

# Rule 10

Preserve naming conventions.

Never rename:

- Events
- APIs
- Contracts
- Folder names
- Database models

without team approval.

---

# Rule 11

All breaking changes require coordination.

If a breaking change is unavoidable:

- Document it.
- Update the contract.
- Notify the other developers before implementation.

---

# Rule 12

Do not introduce new technologies unless the team agrees.

Work within the existing architecture.

---

# Rule 13

Keep commits focused.

Each commit should represent one logical change.

Avoid mixing unrelated work.

---

# Rule 14

Maintain backward compatibility.

New features should not break existing functionality.

---

# Rule 15

Every module must be independently deployable and testable.

Dependencies between modules should exist only through documented interfaces.

---

# Rule 16

Documentation is required.

Every feature must include:

- Overview
- Architecture
- API (if applicable)
- Events (if applicable)
- Examples
- Integration Guide

---

# Rule 17

If another developer's functionality is required, define only the dependency.

For Backend:

Required Endpoint

Request

Response

For AI:

Required Prompt

Context

Memory API

For Frontend:

Required Component

State

Props

Never implement another developer's responsibility.

---

# Rule 18

The objective is one consistent codebase.

Individual optimization must never come at the cost of architectural consistency.

Protect long-term maintainability over short-term convenience.