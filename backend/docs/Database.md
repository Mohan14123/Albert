# 03 - Database Design

**Project:** AI Personal Assistant  
**Version:** 1.0  
**Owner:** Backend Team  
**Database:** PostgreSQL 16  
**ORM:** SQLAlchemy 2.0  
**Migration Tool:** Alembic  
**Last Updated:** 18 July 2026

---

# 1. Purpose

This document defines the database architecture, relationships, constraints, indexing strategy, and conventions used throughout the backend.

The database is designed to be:

- Scalable
- Secure
- Normalized
- Easy to maintain
- AI-ready
- Integration-ready

---

# 2. Database Overview

```
PostgreSQL

│

├── Users
├── Refresh Tokens
├── Chats
├── Messages
├── User Settings
├── Integrations
├── OAuth Tokens
├── Files (Future)
├── Memory (Future)
└── Notifications (Future)
```

---

# 3. Entity Relationship Diagram

```
Users
│
├──── RefreshTokens
│
├──── Chats
│       │
│       └──── Messages
│
├──── UserSettings
│
└──── Integrations
         │
         └──── OAuthTokens
```

---

# 4. Table Naming Convention

- Singular table names are **not** used.
- All table names are plural.
- Snake case only.

Example

```
users
messages
refresh_tokens
oauth_tokens
```

---

# 5. Common Columns

Every table should contain:

| Column | Type |
|----------|------|
| id | UUID |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

Optional

```
deleted_at
```

Soft deletes should be preferred over permanent deletion for user-generated content.

---

# 6. Users Table

Table

```
users
```

| Column | Type | Description |
|----------|------|-------------|
| id | UUID | Primary Key |
| email | VARCHAR(255) | Unique |
| password_hash | TEXT | Argon2 Hash |
| full_name | VARCHAR(100) | User Name |
| assistant_name | VARCHAR(50) | Assistant Alias |
| timezone | VARCHAR(50) | User Timezone |
| language | VARCHAR(20) | Preferred Language |
| is_active | BOOLEAN | Active Account |
| created_at | TIMESTAMP | Creation Time |
| updated_at | TIMESTAMP | Last Update |

Indexes

```
email UNIQUE
```

---

# 7. Refresh Tokens

Table

```
refresh_tokens
```

| Column | Type |
|----------|------|
| id | UUID |
| user_id | UUID |
| token_hash | TEXT |
| expires_at | TIMESTAMP |
| revoked | BOOLEAN |
| created_at | TIMESTAMP |

Relationships

```
User

1

↓

Many Refresh Tokens
```

---

# 8. Chats

Table

```
chats
```

| Column | Type |
|----------|------|
| id | UUID |
| user_id | UUID |
| title | VARCHAR(255) |
| archived | BOOLEAN |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

Relationship

```
User

↓

Many Chats
```

---

# 9. Messages

Table

```
messages
```

| Column | Type |
|----------|------|
| id | UUID |
| chat_id | UUID |
| role | ENUM |
| content | TEXT |
| status | ENUM |
| token_count | INTEGER |
| created_at | TIMESTAMP |

Role

```
user

assistant

system
```

Status

```
pending

completed

failed
```

Relationship

```
Chat

↓

Many Messages
```

Indexes

```
chat_id

created_at
```

---

# 10. User Settings

Table

```
user_settings
```

| Column | Type |
|----------|------|
| id | UUID |
| user_id | UUID |
| theme | VARCHAR |
| language | VARCHAR |
| notifications | BOOLEAN |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

Relationship

```
User

↓

One Settings Record
```

---

# 11. Integrations

Table

```
integrations
```

| Column | Type |
|----------|------|
| id | UUID |
| user_id | UUID |
| provider | VARCHAR |
| status | ENUM |
| connected_at | TIMESTAMP |
| last_sync | TIMESTAMP |

Status

```
connected

expired

disconnected
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

---

# 12. OAuth Tokens

Table

```
oauth_tokens
```

Sensitive table.

Tokens should always be encrypted before storage.

| Column | Type |
|----------|------|
| id | UUID |
| integration_id | UUID |
| access_token | TEXT (Encrypted) |
| refresh_token | TEXT (Encrypted) |
| expires_at | TIMESTAMP |
| created_at | TIMESTAMP |

Relationship

```
Integration

↓

OAuth Tokens
```

---

# 13. Future Tables

## Files

```
files
```

Stores

- Uploaded documents
- Images
- Audio
- Videos

---

## File Chunks

```
file_chunks
```

Stores

- Extracted text
- Metadata
- Embedding IDs

---

## Memory

```
memories
```

Stores

- Conversation summaries
- Facts
- Preferences
- Tasks

---

## Embeddings

```
embeddings
```

Stores

- Vector IDs
- Source IDs
- Similarity metadata

---

## Notifications

```
notifications
```

Stores

- Push notifications
- Email notifications
- Reminder events

---

# 14. Relationships

```
Users

│

├──── Chats

│      └──── Messages

│

├──── Refresh Tokens

│

├──── User Settings

│

└──── Integrations

        └──── OAuth Tokens
```

---

# 15. UUID Strategy

All primary keys use UUID v7 (preferred) or UUID v4 if unsupported.

Reasons

- Globally unique
- Distributed systems
- Easier sharding
- More secure than sequential IDs

---

# 16. Constraints

Every foreign key should enforce integrity.

Examples

```
messages.chat_id

↓

REFERENCES chats(id)
```

```
chats.user_id

↓

REFERENCES users(id)
```

---

# 17. Cascading Rules

Recommended

```
User Deleted

↓

Chats Deleted

↓

Messages Deleted
```

OAuth Tokens

```
Integration Deleted

↓

OAuth Tokens Deleted
```

Refresh Tokens

```
User Deleted

↓

Refresh Tokens Deleted
```

---

# 18. Index Strategy

Indexes should exist on:

```
users.email

messages.chat_id

messages.created_at

refresh_tokens.user_id

integrations.user_id

oauth_tokens.integration_id

chats.user_id
```

Composite indexes

```
(chat_id, created_at)

(user_id, provider)
```

---

# 19. Database Transactions

Use transactions for:

- Registration
- Login
- OAuth Connection
- Chat Creation
- Message Creation
- Integration Sync

Example

```
Create Chat

↓

Insert Chat

↓

Insert First Message

↓

Publish Event

↓

Commit
```

Rollback on failure.

---

# 20. Encryption

Sensitive fields

```
OAuth Tokens

Refresh Tokens

API Keys
```

Encryption

```
AES-256

Key stored separately
```

Passwords are **never encrypted**.

Passwords are always hashed using Argon2.

---

# 21. Migration Strategy

Use Alembic.

Migration naming

```
001_create_users

002_create_chat

003_create_messages

004_create_integrations

005_create_tokens
```

Never modify old migrations.

Always create new migration files.

---

# 22. Performance Guidelines

Avoid

```
SELECT *
```

Prefer

- Pagination
- Indexes
- Prepared statements
- Connection pooling

Chat history should always use pagination.

---

# 23. Backup Strategy

Daily

- Full Database Backup

Hourly

- WAL Archiving

Weekly

- Backup Verification

Retention

```
30 Days
```

---

# 24. Database Standards

- UUID primary keys
- Foreign keys everywhere
- Snake case
- Soft delete where appropriate
- UTC timestamps only
- No business logic in SQL
- SQLAlchemy ORM only
- Parameterized queries
- Encrypted sensitive data
- Indexed search fields

---

# 25. Initial Schema

```
users

refresh_tokens

chats

messages

user_settings

integrations

oauth_tokens
```

Future

```
files

file_chunks

memories

embeddings

notifications
```

---

# 26. Definition of Done

The database layer is complete when:

- All tables are created through Alembic migrations.
- UUID primary keys are used consistently.
- Relationships are enforced with foreign keys.
- Sensitive data is encrypted or hashed appropriately.
- Indexes support expected query patterns.
- All timestamps are stored in UTC.
- The schema supports backend, AI, and future integrations without requiring breaking changes.

---

**End of Document**