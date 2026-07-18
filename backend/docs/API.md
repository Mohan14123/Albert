# 04 - Backend API Specification

**Project:** AI Personal Assistant  
**Version:** 1.0  
**Owner:** Backend Team  
**Protocol:** REST + Server-Sent Events (SSE)  
**Format:** JSON  
**Authentication:** JWT Bearer Token  
**Last Updated:** 18 July 2026

---

# 1. Purpose

This document defines every backend API exposed by the platform.

It serves as the contract between:

- Backend Team
- Frontend Team
- AI Team

All teams should rely on this document instead of inspecting backend code.

---

# 2. API Standards

## Base URL

```
/api/v1
```

Example

```
/api/v1/auth/login
```

---

## Authentication

Protected endpoints require

```
Authorization: Bearer <JWT_TOKEN>
```

---

## Content Type

```
application/json
```

Streaming

```
text/event-stream
```

---

# 3. Standard Response Format

## Success

```json
{
  "success": true,
  "data": {}
}
```

---

## Error

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid input."
  }
}
```

---

# 4. Authentication APIs

---

## Register

```
POST /api/v1/auth/register
```

### Request

```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "user_id": "uuid"
  }
}
```

---

## Login

```
POST /api/v1/auth/login
```

### Request

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "expires_in": 3600
  }
}
```

---

## Refresh Token

```
POST /api/v1/auth/refresh
```

### Request

```json
{
  "refresh_token": "..."
}
```

---

## Logout

```
POST /api/v1/auth/logout
```

Revokes refresh token.

---

## Get Current User

```
GET /api/v1/auth/me
```

---

# 5. User APIs

---

## Get Profile

```
GET /api/v1/users/me
```

---

## Update Profile

```
PATCH /api/v1/users/me
```

### Request

```json
{
  "full_name": "John Doe",
  "assistant_name": "Albert",
  "timezone": "Asia/Kolkata"
}
```

---

## Get Settings

```
GET /api/v1/users/settings
```

---

## Update Settings

```
PATCH /api/v1/users/settings
```

---

# 6. Chat APIs

---

## Create Chat

```
POST /api/v1/chats
```

### Request

```json
{
  "title": "Project Discussion"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "chat_id": "uuid"
  }
}
```

---

## Get Chats

```
GET /api/v1/chats
```

Supports pagination.

Query

```
?page=1

&limit=20
```

---

## Get Chat

```
GET /api/v1/chats/{chat_id}
```

---

## Rename Chat

```
PATCH /api/v1/chats/{chat_id}
```

---

## Delete Chat

```
DELETE /api/v1/chats/{chat_id}
```

Soft delete.

---

# 7. Message APIs

---

## Send Message

```
POST /api/v1/chats/{chat_id}/messages
```

### Request

```json
{
  "content": "What meetings do I have today?"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "message_id": "uuid",
    "status": "processing"
  }
}
```

Publishing this request triggers the AI service asynchronously.

---

## Get Messages

```
GET /api/v1/chats/{chat_id}/messages
```

Supports pagination.

```
?page=1

&limit=50
```

---

## Stream AI Response (SSE)

```
GET /api/v1/chats/{chat_id}/stream
```

Response

```
text/event-stream
```

Example

```
event: token

data: Hello

event: token

data: world

event: done

data: complete
```

---

# 8. Integration APIs

---

## List Integrations

```
GET /api/v1/integrations
```

---

## Connect Provider

```
POST /api/v1/integrations/{provider}/connect
```

Providers

```
gmail

calendar

slack

jira

github

notion
```

Returns OAuth redirect URL.

---

## OAuth Callback

```
GET /api/v1/integrations/{provider}/callback
```

---

## Disconnect

```
DELETE /api/v1/integrations/{provider}
```

---

## Manual Sync

```
POST /api/v1/integrations/{provider}/sync
```

Starts background synchronization.

---

## Sync Status

```
GET /api/v1/integrations/{provider}/status
```

---

# 9. File APIs (Future)

---

## Upload File

```
POST /api/v1/files
```

Multipart request.

---

## List Files

```
GET /api/v1/files
```

---

## Delete File

```
DELETE /api/v1/files/{id}
```

---

# 10. Notification APIs (Future)

---

## Get Notifications

```
GET /api/v1/notifications
```

---

## Mark Read

```
PATCH /api/v1/notifications/{id}
```

---

# 11. Health APIs

---

## Health Check

```
GET /api/v1/health
```

Response

```json
{
  "status": "healthy"
}
```

---

## Readiness Check

```
GET /api/v1/ready
```

Checks

- Database
- Redis
- RabbitMQ

---

## Version

```
GET /api/v1/version
```

---

# 12. AI APIs (Internal)

These endpoints are intended for the AI service.

---

## Generate Response

```
POST /internal/ai/respond
```

Backend sends

```json
{
  "chat_id": "uuid",
  "user_id": "uuid",
  "message": "...",
  "context": {}
}
```

---

## AI Callback

```
POST /internal/ai/callback
```

AI returns

```json
{
  "message": "...",
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 80
  }
}
```

---

# 13. Webhooks

---

## Gmail

```
POST /webhooks/gmail
```

---

## Calendar

```
POST /webhooks/calendar
```

---

## Slack

```
POST /webhooks/slack
```

---

## Jira

```
POST /webhooks/jira
```

---

# 14. HTTP Status Codes

| Code | Meaning |
|--------|----------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |

---

# 15. Pagination Standard

Every list endpoint uses

```
?page=1

&limit=20
```

Response

```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 200,
    "pages": 10
  }
}
```

---

# 16. Error Codes

| Code | Description |
|--------|-------------|
| INVALID_REQUEST | Invalid payload |
| INVALID_TOKEN | JWT invalid |
| TOKEN_EXPIRED | JWT expired |
| NOT_FOUND | Resource missing |
| PERMISSION_DENIED | Unauthorized action |
| RATE_LIMITED | Too many requests |
| PROVIDER_ERROR | Integration failure |
| INTERNAL_ERROR | Unexpected server error |

---

# 17. Rate Limits

| Endpoint | Limit |
|-----------|-------|
| Login | 5/min/IP |
| Register | 3/min/IP |
| Chat | 60/min/user |
| Messages | 120/min/user |
| Integrations | 10/min/user |

---

# 18. API Versioning

Current

```
/api/v1
```

Future

```
/api/v2
```

Breaking changes require a new version.

---

# 19. OpenAPI

Swagger UI

```
/docs
```

OpenAPI JSON

```
/openapi.json
```

These are generated automatically by FastAPI and remain the authoritative machine-readable API specification.

---

# 20. Definition of Done

The API layer is complete when:

- All endpoints are implemented.
- JWT authentication protects private routes.
- OpenAPI documentation is generated.
- Pagination is consistent.
- Error responses follow the standard format.
- Streaming endpoints use SSE.
- Internal AI endpoints are documented.
- Integration webhooks are available.
- Frontend and AI teams can integrate without backend changes.

---

**End of Document**