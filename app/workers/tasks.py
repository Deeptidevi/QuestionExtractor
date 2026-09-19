from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.processing.pipeline import DocumentProcessor
from app.core.logging import logger


@celery_app.task(bind=True, name="tasks.process_document", max_retries=2, default_retry_delay=10)
def process_document_task(self, document_id: str, job_id: str):
    """
    Celery background worker task for processing a document asynchronously.
    """
    logger.info(f"Celery worker received job {job_id} for document {document_id}")
    db = SessionLocal()
    try:
        processor = DocumentProcessor(db=db)
        doc = processor.process_document(document_id=document_id, job_id=job_id)
        return {
            "status": doc.status.value,
            "document_id": doc.id,
            "total_pages": doc.total_pages,
            "overall_confidence": doc.overall_confidence,
        }
    except Exception as exc:
        logger.error(f"Celery task failed for document {document_id}: {exc}", exc_info=True)
        # Attempt retry if retry count not exceeded
        try:
            raise self.retry(exc=exc)
        except Exception:
            raise exc
    finally:
        db.close()
