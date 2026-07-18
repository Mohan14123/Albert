# 08 - Deployment & Infrastructure Guide

**Project:** AI Personal Assistant  
**Version:** 1.0  
**Owner:** Backend Team  
**Environment:** Local • Development • Staging • Production  
**Last Updated:** 18 July 2026

---

# 1. Purpose

This document describes how the backend is deployed, configured, monitored, and maintained across all environments.

Goals:

- Reproducible deployments
- Scalable infrastructure
- High availability
- Secure configuration
- Easy onboarding
- Zero manual setup

---

# 2. Infrastructure Overview

```
                    Internet
                        │
                        ▼
                  Reverse Proxy
                     (Nginx)
                        │
        ┌───────────────┼───────────────┐
        │                               │
        ▼                               ▼
 FastAPI Backend                  Static Frontend
        │
        ▼
     RabbitMQ
        │
        ▼
 Background Workers
        │
        ▼
   PostgreSQL + Redis
        │
        ▼
 External Services
(Gmail, Calendar, Slack, GitHub)
```

---

# 3. Environments

## Local

Purpose

- Development
- Debugging
- Feature implementation

Runs

```
Backend

PostgreSQL

Redis

RabbitMQ

PgAdmin (optional)

MailHog (optional)
```

---

## Development

Purpose

- Team integration
- Feature testing

Runs

```
Docker Compose

Shared Database

Shared Redis

Shared RabbitMQ
```

---

## Staging

Purpose

- Final QA
- Production testing

Runs

```
Production-like infrastructure

HTTPS

Monitoring

Real Integrations (Sandbox)
```

---

## Production

Purpose

```
Live Application
```

Requirements

- HTTPS
- Monitoring
- Auto Scaling
- Backups
- Secret Management

---

# 4. Technology Stack

| Component | Technology |
|------------|------------|
| API | FastAPI |
| Database | PostgreSQL 16 |
| Cache | Redis |
| Message Broker | RabbitMQ |
| Reverse Proxy | Nginx |
| Containers | Docker |
| Orchestration (Future) | Kubernetes |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus |
| Dashboards | Grafana |
| Logging | Loki / ELK |
| Object Storage (Future) | MinIO / Amazon S3 |

---

# 5. Docker Architecture

```
docker-compose.yml

│

├── backend

├── postgres

├── redis

├── rabbitmq

├── worker

├── nginx

└── pgadmin (optional)
```

---

# 6. Container Responsibilities

## Backend

Runs

- FastAPI
- API Routes
- Authentication
- Services

Port

```
8000
```

---

## PostgreSQL

Stores

- Users
- Chats
- Messages
- Integrations

Port

```
5432
```

---

## Redis

Stores

- Cache
- Sessions
- Rate Limits

Port

```
6379
```

---

## RabbitMQ

Stores

- Events
- Queues

Ports

```
5672

15672 (Dashboard)
```

---

## Worker

Runs

- Celery Workers
- Background Jobs
- Sync Tasks
- Notifications

---

## Nginx

Responsibilities

- HTTPS
- Reverse Proxy
- Compression
- Security Headers
- Load Balancing (Future)

Port

```
80

443
```

---

# 7. Folder Structure

```
backend/

docker/

│

├── backend.Dockerfile

├── worker.Dockerfile

├── nginx.conf

├── docker-compose.yml

├── docker-compose.prod.yml

└── .env.example
```

---

# 8. Environment Variables

## Application

```env
APP_NAME=AI Assistant

ENVIRONMENT=development

DEBUG=true
```

---

## Database

```env
DATABASE_URL=

POSTGRES_USER=

POSTGRES_PASSWORD=

POSTGRES_DB=
```

---

## Redis

```env
REDIS_URL=
```

---

## RabbitMQ

```env
RABBITMQ_URL=
```

---

## Authentication

```env
JWT_SECRET=

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=15

REFRESH_TOKEN_EXPIRE_DAYS=30
```

---

## OAuth

```env
GOOGLE_CLIENT_ID=

GOOGLE_CLIENT_SECRET=

GITHUB_CLIENT_ID=

GITHUB_CLIENT_SECRET=
```

---

## AI

```env
OPENAI_API_KEY=

AI_SERVICE_URL=
```

---

# 9. Startup Sequence

```
PostgreSQL

↓

Redis

↓

RabbitMQ

↓

Backend

↓

Workers

↓

Nginx
```

Containers should wait for dependencies before starting.

---

# 10. Health Checks

Backend

```
GET /api/v1/health
```

Returns

```json
{
    "status": "healthy"
}
```

---

Readiness

```
GET /api/v1/ready
```

Checks

- PostgreSQL
- Redis
- RabbitMQ

---

Docker Health Check

Example

```
curl http://localhost:8000/api/v1/health
```

---

# 11. Database Migrations

Migration Tool

```
Alembic
```

Deployment flow

```
Start Container

↓

Run Alembic Upgrade

↓

Start FastAPI
```

No manual migrations in production.

---

# 12. Logging

Use structured JSON logging.

Every log includes

```
Timestamp

Request ID

User ID

Service

Status

Duration

Level
```

Never log

- Passwords
- OAuth Tokens
- JWT Secrets
- API Keys

---

# 13. Monitoring

Metrics

- CPU Usage
- Memory Usage
- API Latency
- Error Rate
- Queue Size
- Worker Status
- Database Connections

Expose metrics

```
/metrics
```

Consumed by

```
Prometheus
```

---

# 14. Alerting

Critical alerts

- Backend unavailable
- Database unavailable
- Redis unavailable
- RabbitMQ unavailable
- Worker stopped
- High error rate
- High queue backlog
- Disk usage > 80%

---

# 15. Backup Strategy

Database

Daily full backup

Hourly WAL archive

Retention

```
30 Days
```

---

Configuration

Backup

- Environment templates
- Docker Compose
- Nginx configuration

---

# 16. Scaling Strategy

Current

```
Single Backend

Single Database

Single Worker
```

Future

```
Load Balancer

↓

Multiple FastAPI Instances

↓

RabbitMQ Cluster

↓

Redis Cluster

↓

PostgreSQL Read Replicas

↓

Dedicated AI Cluster
```

Backend remains stateless to support horizontal scaling.

---

# 17. Security

Infrastructure requirements

- HTTPS only
- TLS 1.3
- Strong CORS policy
- Secure cookies
- Environment-based secrets
- Rate limiting
- Firewall rules
- Fail2Ban (optional)
- Reverse proxy security headers

---

# 18. CI/CD Pipeline

Pipeline

```
Git Push

↓

GitHub Actions

↓

Lint

↓

Type Check

↓

Unit Tests

↓

Integration Tests

↓

Build Docker Image

↓

Deploy

↓

Run Migrations

↓

Health Check
```

Deployment proceeds only if every stage passes.

---

# 19. Local Development

Start services

```bash
docker compose up --build
```

Stop

```bash
docker compose down
```

Run migrations

```bash
alembic upgrade head
```

Run backend

```bash
uvicorn app.main:app --reload
```

---

# 20. Production Checklist

Before deployment

- Environment variables configured
- Secrets stored securely
- HTTPS enabled
- Database backups verified
- Health checks passing
- Monitoring enabled
- Logging configured
- Migrations applied
- Workers running
- RabbitMQ healthy
- Redis healthy

---

# 21. Disaster Recovery

Recovery order

```
Restore Database

↓

Restore Redis (optional)

↓

Restart RabbitMQ

↓

Deploy Backend

↓

Run Health Checks
```

Verify

- User login
- Chat creation
- Message processing
- Integrations
- Worker queues

---

# 22. Maintenance

Weekly

- Review logs
- Check backups
- Verify SSL certificates
- Update dependencies
- Review failed jobs

Monthly

- Security patches
- Database optimization
- Queue cleanup
- Storage audit

---

# 23. Definition of Done

The deployment infrastructure is complete when:

- Docker Compose starts all services successfully.
- Health and readiness checks pass.
- Environment variables are fully documented.
- Alembic migrations run automatically.
- CI/CD pipeline builds, tests, and deploys successfully.
- Monitoring and logging are enabled.
- Backups are configured and tested.
- The backend can scale horizontally without code changes.
- Production secrets are managed securely.
- The platform is ready for AI, frontend, and integration services.

---

**End of Document**