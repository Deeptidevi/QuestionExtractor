#!/usr/bin/env bash
set -e

echo "==> Running Alembic Database Migrations..."
alembic upgrade head

echo "==> Starting Background Celery Worker..."
celery -A app.workers.celery_app worker --loglevel=info --concurrency=2 &

echo "==> Starting FastAPI Uvicorn Web Server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
