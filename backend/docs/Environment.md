# 10 - Environment Configuration Guide

**Project:** AI Personal Assistant  
**Version:** 1.0  
**Owner:** Backend Team  
**Last Updated:** 18 July 2026

---

# 1. Purpose

This document defines every environment variable used by the backend.

Goals:

- Consistent configuration across environments
- Secure secret management
- Easy onboarding
- Production-ready deployments
- Zero hardcoded configuration

All application configuration must come from environment variables.

---

# 2. Environment Strategy

The project supports four environments.

```
Local

↓

Development

↓

Staging

↓

Production
```

Each environment has its own configuration.

Example

```
.env

.env.local

.env.development

.env.staging

.env.production
```

Production secrets must never exist inside the repository.

---

# 3. Loading Configuration

FastAPI loads configuration using Pydantic Settings.

```
Environment Variables

↓

Pydantic Settings

↓

Application Configuration
```

Configuration should be loaded once during application startup.

---

# 4. Application Settings

```env
APP_NAME=AI Personal Assistant

APP_VERSION=1.0.0

ENVIRONMENT=development

DEBUG=true

API_PREFIX=/api/v1
```

---

# 5. Server Settings

```env
HOST=0.0.0.0

PORT=8000

WORKERS=4

LOG_LEVEL=INFO
```

Production should run multiple workers behind a reverse proxy.

---

# 6. Database

```env
DATABASE_URL=postgresql+psycopg://user:password@postgres:5432/assistant

POSTGRES_DB=assistant

POSTGRES_USER=assistant

POSTGRES_PASSWORD=change_me

DATABASE_POOL_SIZE=20

DATABASE_MAX_OVERFLOW=40
```

Never commit production credentials.

---

# 7. Redis

```env
REDIS_URL=redis://redis:6379/0

REDIS_CACHE_TTL=3600
```

Used for

- Cache
- Rate limiting
- Session metadata
- Temporary state

---

# 8. RabbitMQ

```env
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

RABBITMQ_EXCHANGE=assistant.exchange
```

Used for

- Domain events
- Background jobs
- Queue communication

---

# 9. JWT Configuration

```env
JWT_SECRET=CHANGE_THIS

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=15

REFRESH_TOKEN_EXPIRE_DAYS=30
```

JWT secrets should be generated using a cryptographically secure random value.

---

# 10. Password Hashing

```env
PASSWORD_HASHER=argon2

ARGON2_TIME_COST=3

ARGON2_MEMORY_COST=65536

ARGON2_PARALLELISM=4
```

These values may be tuned based on hardware.

---

# 11. OAuth Providers

## Google

```env
GOOGLE_CLIENT_ID=

GOOGLE_CLIENT_SECRET=

GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/integrations/google/callback
```

---

## GitHub

```env
GITHUB_CLIENT_ID=

GITHUB_CLIENT_SECRET=

GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/integrations/github/callback
```

---

## Microsoft

```env
MICROSOFT_CLIENT_ID=

MICROSOFT_CLIENT_SECRET=

MICROSOFT_REDIRECT_URI=http://localhost:8000/api/v1/integrations/microsoft/callback
```

---

# 12. AI Service

```env
AI_SERVICE_URL=http://ai-service:8001

AI_API_KEY=

AI_REQUEST_TIMEOUT=120
```

The backend communicates with the AI service through this endpoint.

---

# 13. Token Encryption

```env
TOKEN_ENCRYPTION_KEY=
```

Used to encrypt

- OAuth Tokens
- API Credentials
- Integration Secrets

Recommended

```
AES-256 Key
```

---

# 14. File Storage

Local Development

```env
FILE_STORAGE=local

UPLOAD_DIRECTORY=uploads/
```

Future

```env
FILE_STORAGE=s3

AWS_ACCESS_KEY_ID=

AWS_SECRET_ACCESS_KEY=

AWS_REGION=

S3_BUCKET=
```

---

# 15. Email Service (Future)

```env
SMTP_HOST=

SMTP_PORT=587

SMTP_USERNAME=

SMTP_PASSWORD=

SMTP_FROM=
```

Used for

- Password reset
- Notifications
- Verification emails

---

# 16. Monitoring

```env
PROMETHEUS_ENABLED=true

METRICS_PATH=/metrics
```

Logging

```env
LOG_FORMAT=json

REQUEST_ID_HEADER=X-Request-ID
```

---

# 17. CORS

```env
CORS_ORIGINS=http://localhost:3000

CORS_ALLOW_CREDENTIALS=true
```

Production should explicitly list trusted frontend domains.

---

# 18. Rate Limiting

```env
RATE_LIMIT_ENABLED=true

LOGIN_RATE_LIMIT=5/minute

API_RATE_LIMIT=100/minute
```

Implemented using Redis.

---

# 19. Feature Flags

```env
ENABLE_VOICE=false

ENABLE_FILE_UPLOAD=true

ENABLE_NOTIFICATIONS=false

ENABLE_MEMORY=true

ENABLE_RAG=true
```

Feature flags allow gradual rollout without code changes.

---

# 20. Security

Never expose

```
JWT_SECRET

CLIENT_SECRET

API_KEYS

DATABASE_PASSWORD

TOKEN_ENCRYPTION_KEY
```

Never print secrets in logs.

Never return secrets through APIs.

---

# 21. Local Example

Example

```env
APP_NAME=AI Personal Assistant

ENVIRONMENT=development

DEBUG=true

DATABASE_URL=postgresql+psycopg://assistant:password@postgres:5432/assistant

REDIS_URL=redis://redis:6379/0

RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

JWT_SECRET=replace_with_secure_random_secret

ACCESS_TOKEN_EXPIRE_MINUTES=15

REFRESH_TOKEN_EXPIRE_DAYS=30

AI_SERVICE_URL=http://localhost:8001

CORS_ORIGINS=http://localhost:3000
```

---

# 22. Production Recommendations

- Use a secrets manager (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault, etc.).
- Disable `DEBUG`.
- Enable HTTPS only.
- Restrict CORS origins.
- Rotate secrets regularly.
- Use strong random values for all cryptographic keys.
- Encrypt backups containing sensitive data.

---

# 23. Validation Rules

At startup the application should validate:

- Required variables exist.
- URLs are valid.
- Secrets are not empty.
- Numeric values are within expected ranges.
- Environment is one of:

```
local

development

staging

production
```

The application should fail fast if configuration is invalid.

---

# 24. .env.example

```env
APP_NAME=AI Personal Assistant
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

HOST=0.0.0.0
PORT=8000

DATABASE_URL=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

REDIS_URL=

RABBITMQ_URL=

JWT_SECRET=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

TOKEN_ENCRYPTION_KEY=

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=

AI_SERVICE_URL=
AI_API_KEY=

CORS_ORIGINS=http://localhost:3000

RATE_LIMIT_ENABLED=true

PROMETHEUS_ENABLED=true
```

---

# 25. Definition of Done

Environment configuration is complete when:

- All configuration is externalized.
- No secrets are hardcoded.
- Every required variable is documented.
- Startup validation prevents invalid configuration.
- `.env.example` contains all required keys.
- Development, staging, and production environments use separate configuration.
- Secret rotation is supported without code changes.
- The application can be deployed by supplying only environment variables.

---

**End of Document**