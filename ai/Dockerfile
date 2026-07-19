FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY backend/pyproject.toml ./
RUN uv pip install --system fastapi uvicorn aio-pika pydantic-settings

COPY ai ./ai

EXPOSE 8001
CMD ["uvicorn", "ai.main:app", "--host", "0.0.0.0", "--port", "8001"]
