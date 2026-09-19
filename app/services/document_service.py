from typing import BinaryIO, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundException, PermissionDeniedException
from app.db.models.document import Document, DocumentStatus
from app.db.models.document_page import DocumentPage
from app.db.models.processing_job import ProcessingJob
from app.db.models.question import Question
from app.db.models.review_item import ReviewItem
from app.db.repositories.document_repo import DocumentRepository
from app.processing.file_validator import FileValidator
from app.services.storage_service import storage_service
from app.workers.tasks import process_document_task
from app.processing.pipeline import DocumentProcessor
from app.core.config import settings
from app.core.logging import logger


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DocumentRepository(db)

    def upload_document(
        self,
        file_obj: BinaryIO,
        filename: str,
        content_type: str,
        file_size: int,
        user_id: str,
        title: Optional[str] = None,
        sync_process: bool = False,
    ) -> Tuple[Document, ProcessingJob]:
        """
        Validates, securely stores, creates DB records, and dispatches async background worker job.
        """
        # 1. Validate file
        normalized_mime, ext = FileValidator.validate_upload(
            file_obj=file_obj,
            filename=filename,
            content_type=content_type,
            file_size=file_size,
        )

        # 2. Save file through storage abstraction
        rel_path, sha256_hash, total_bytes = storage_service.save_file(
            file_obj=file_obj,
            original_filename=filename,
            content_type=normalized_mime,
        )

        # 3. Create document record
        doc_title = title or filename.rsplit(".", 1)[0]
        doc = Document(
            user_id=user_id,
            title=doc_title,
            original_filename=filename,
            stored_path=rel_path,
            mime_type=normalized_mime,
            file_size=total_bytes,
            file_hash=sha256_hash,
            status=DocumentStatus.QUEUED,
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)

        # 4. Create processing job record
        job = self.repo.create_job(document_id=doc.id)

        # 5. Dispatch task
        if sync_process:
            # Process synchronously (useful for local development or direct test suites)
            processor = DocumentProcessor(db=self.db)
            processor.process_document(document_id=doc.id, job_id=job.id)
            self.db.refresh(doc)
            self.db.refresh(job)
        else:
            try:
                task = process_document_task.delay(document_id=doc.id, job_id=job.id)
                job.celery_task_id = task.id
                self.db.commit()
            except Exception as e:
                logger.warning(
                    f"Celery queue unreachable ({e}); executing synchronous fallback processing."
                )
                processor = DocumentProcessor(db=self.db)
                processor.process_document(document_id=doc.id, job_id=job.id)
                self.db.refresh(doc)
                self.db.refresh(job)

        return doc, job

    def get_document(self, document_id: str, user_id: str) -> Document:
        doc = self.repo.get(document_id)
        if not doc:
            raise ResourceNotFoundException("Document", document_id)
        if doc.user_id != user_id:
            raise PermissionDeniedException("You do not have access to this document.")
        return doc

    def list_documents(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[DocumentStatus] = None,
    ) -> Tuple[List[Document], int]:
        return self.repo.get_by_user(user_id=user_id, skip=skip, limit=limit, status=status)

    def get_document_status(self, document_id: str, user_id: str) -> dict:
        doc = self.get_document(document_id, user_id)
        latest_job = self.repo.get_latest_job(document_id)
        
        # Count questions and review requirements
        total_questions = self.db.query(Question).filter(Question.document_id == doc.id).count()
        review_count = (
            self.db.query(ReviewItem)
            .filter(ReviewItem.document_id == doc.id, ReviewItem.is_resolved.is_(False))
            .count()
        )

        return {
            "document_id": doc.id,
            "status": doc.status,
            "total_pages": doc.total_pages,
            "is_scanned": doc.is_scanned,
            "overall_confidence": doc.overall_confidence,
            "current_job_id": latest_job.id if latest_job else None,
            "job_status": latest_job.status if latest_job else None,
            "current_stage": latest_job.current_stage if latest_job else None,
            "progress_percent": latest_job.progress_percent if latest_job else None,
            "error_summary": latest_job.error_summary if latest_job else None,
            "review_required_count": review_count,
            "total_questions": total_questions,
            "updated_at": doc.updated_at,
        }

    def delete_document(self, document_id: str, user_id: str) -> bool:
        doc = self.get_document(document_id, user_id)
        storage_service.delete_file(doc.stored_path)
        return self.repo.delete(doc.id)
