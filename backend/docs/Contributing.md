# 09 - Backend Development Guidelines

**Project:** AI Personal Assistant  
**Version:** 1.0  
**Owner:** Backend Team  
**Audience:** Backend Developers, AI Developers, Frontend Developers  
**Last Updated:** 18 July 2026

---

# 1. Purpose

This document defines the development standards, coding conventions, Git workflow, review process, and contribution guidelines for the backend.

Every contributor should follow these standards to ensure consistency, maintainability, and scalability.

---

# 2. Core Principles

Every contribution should follow these principles:

- Keep modules independent.
- Write clean, readable code.
- Prefer composition over inheritance.
- Keep functions small and focused.
- Write tests for all business logic.
- Document public APIs.
- Avoid duplicated code.
- Make changes backward compatible whenever possible.

---

# 3. Project Structure

```
backend/

app/
├── api/
├── auth/
├── chat/
├── users/
├── integrations/
├── services/
├── repositories/
├── database/
├── events/
├── workers/
├── middleware/
├── core/
├── config/

tests/

docs/

scripts/

alembic/
```

Every feature should live inside its own module.

---

# 4. Layer Responsibilities

## API Layer

Responsible for

- Routing
- Request validation
- Response formatting
- Dependency injection

Do NOT

- Write SQL
- Perform business logic
- Call external APIs directly

---

## Service Layer

Responsible for

- Business logic
- Validation
- Event publishing
- Calling repositories
- Calling integrations

Do NOT

- Return HTTP responses
- Use FastAPI objects
- Write SQL queries

---

## Repository Layer

Responsible for

- CRUD operations
- Database queries
- Transactions

Do NOT

- Implement business rules
- Publish events
- Access HTTP requests

---

## Worker Layer

Responsible for

- Background processing
- Queue consumption
- Retry handling
- Long-running jobs

---

# 5. Branch Strategy

```
main
│
develop
│
feature/<feature-name>
bugfix/<bug-name>
hotfix/<issue-name>
```

Examples

```
feature/authentication

feature/chat-api

feature/events

bugfix/login-timeout
```

Never commit directly to `main`.

---

# 6. Commit Convention

Use Conventional Commits.

Examples

```
feat(auth): implement JWT login

feat(chat): add chat history API

fix(events): retry failed consumer

docs(api): update authentication endpoints

refactor(database): simplify repository logic

test(auth): add login unit tests
```

---

# 7. Pull Request Checklist

Every PR must:

- Build successfully
- Pass all tests
- Pass linting
- Include documentation updates (if required)
- Include migration (if database changed)
- Have descriptive title
- Have at least one reviewer approval

---

# 8. Code Style

Language

```
Python 3.12
```

Formatting

```
Black
```

Linting

```
Ruff
```

Type Checking

```
MyPy
```

Naming conventions

Variables

```
snake_case
```

Classes

```
PascalCase
```

Constants

```
UPPER_CASE
```

Private members

```
_prefix
```

---

# 9. Function Guidelines

Functions should:

- Perform one task
- Be easy to test
- Have clear names
- Return predictable results

Avoid

```
process_everything()
```

Prefer

```
validate_user()

create_chat()

publish_event()

save_message()
```

---

# 10. Dependency Injection

Always inject dependencies.

Good

```
ChatService(repository)
```

Avoid

```
ChatService()

↓

Creates Repository Internally
```

Benefits

- Easier testing
- Lower coupling
- Better maintainability

---

# 11. Error Handling

Use custom exceptions.

Example

```
AuthenticationError

ValidationError

NotFoundError

ProviderError
```

Global exception middleware converts them into standard API responses.

Never expose stack traces to clients.

---

# 12. Logging

Log

- Requests
- Errors
- Events
- Background jobs

Never log

- Passwords
- JWTs
- OAuth tokens
- API keys

Every log should include

```
Request ID

Timestamp

Log Level

Service

Message
```

---

# 13. API Standards

Every endpoint should

- Validate input with Pydantic
- Return consistent JSON
- Use HTTP status codes correctly
- Be documented automatically

Response format

```json
{
  "success": true,
  "data": {}
}
```

---

# 14. Database Standards

- UUID primary keys
- UTC timestamps
- Foreign keys
- Alembic migrations only
- SQLAlchemy ORM
- No raw SQL unless necessary

Every schema change requires a migration.

---

# 15. Event Standards

Events must:

- Have unique IDs
- Include correlation IDs
- Be idempotent
- Be versioned
- Use documented payloads

Publish events only after successful database transactions.

---

# 16. Security Standards

- Hash passwords with Argon2id
- Encrypt OAuth tokens
- Validate JWTs
- Enable HTTPS in production
- Use rate limiting
- Sanitize user input
- Store secrets in environment variables

---

# 17. Testing Standards

Minimum coverage target

```
80%
```

Required test types

## Unit

- Services
- Repositories
- Utilities

## Integration

- Authentication
- Database
- APIs
- Events

## End-to-End

- Register
- Login
- Create Chat
- Send Message
- Stream Response

---

# 18. Documentation Standards

Every public module should include:

- Purpose
- Dependencies
- Usage
- Example

Every API change must update

```
04-API.md
```

Every database change must update

```
03-Database.md
```

---

# 19. Git Workflow

```
Create Feature Branch

↓

Implement Feature

↓

Run Tests

↓

Commit

↓

Push

↓

Open Pull Request

↓

Review

↓

Merge into Develop
```

Only tested code should be merged.

---

# 20. Development Checklist

Before pushing code:

- Project builds successfully
- Tests pass
- Ruff passes
- Black formatting applied
- MyPy passes
- No secrets committed
- Documentation updated
- Migration created (if needed)

---

# 21. Review Checklist

Reviewer verifies:

- Architecture compliance
- Naming consistency
- Code readability
- Security implications
- Performance concerns
- Test coverage
- Documentation updates

---

# 22. Definition of Done

A task is complete when:

- Feature works as expected.
- Unit and integration tests pass.
- Code follows project conventions.
- Documentation is updated.
- No linting or type errors remain.
- Pull request is approved and merged.
- No critical security or performance issues are introduced.

---

# 23. Contact Points

| Area | Owner |
|--------|-------|
| Authentication | Backend Lead |
| Database | Backend Lead |
| APIs | Backend Lead |
| Event Bus | Backend Lead |
| Integrations | Backend Lead |
| AI Engine | AI Lead |
| Frontend | Frontend Lead |
| UI/UX | Frontend Team |

---

# 24. Future Improvements

Planned engineering improvements:

- Repository templates
- Automated API contract validation
- Database migration validation
- Event schema registry
- Performance benchmarking
- Security scanning (SAST/DAST)
- Automated dependency updates
- Kubernetes deployment manifests
- Chaos testing
- Load testing pipeline

---

**End of Document**