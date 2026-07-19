FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY app ./app
RUN uv pip install --system -e .

CMD ["python", "-m", "app.workers.scheduler"]
