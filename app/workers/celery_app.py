from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "document_processor_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes maximum processing per document
    worker_prefetch_multiplier=1,  # Prevent worker from hogging large document tasks
    task_acks_late=True,  # Re-queue on unhandled worker crash
)
