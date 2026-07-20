# Deployment Guide

The Albert AI Assistant is structured as a dual-microservice architecture (Backend + AI) along with supporting infrastructure (PostgreSQL, Redis, RabbitMQ). 

## 1. Prerequisites
- Docker & Docker Compose
- AWS CLI (for remote deployment)
- OpenAI API Key

## 2. Local Deployment
The easiest way to run the stack locally is via Docker Compose.

```bash
# 1. Copy the environment variables
cp .env.example .env

# 2. Update .env with your secrets (JWT_SECRET, TOKEN_ENCRYPTION_KEY, AI_API_KEY)

# 3. Start the infrastructure
docker-compose up -d postgres redis rabbitmq

# 4. Run database migrations
# Ensure you run this inside the backend container or virtual environment
alembic upgrade head

# 5. Start the full application
docker-compose up -d
```

## 3. AWS ECS Deployment
A GitHub Actions workflow (`.github/workflows/main.yml`) is provided for automated deployment to AWS Elastic Container Service (ECS).

### Setup AWS Infrastructure:
1. Create two ECR repositories: `albert-backend` and `albert-ai`.
2. Create an ECS Cluster `albert-cluster`.
3. Create an ECS Fargate Service `albert-backend-service`.
4. Configure an RDS PostgreSQL instance (must install `pgvector`), ElastiCache Redis, and Amazon MQ (RabbitMQ).

### Configure GitHub Secrets:
Add the following secrets to your GitHub repository:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Upon pushing to the `main` branch, the CI/CD pipeline will automatically build and push the Docker images to ECR.

## 4. RAG and Vector DB
The system relies on the `pgvector` extension. Our Docker Compose file uses `ankane/pgvector:v0.5.1`. If using Amazon RDS, ensure you enable the `vector` extension by running:
```sql
CREATE EXTENSION vector;
```
