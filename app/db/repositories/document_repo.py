from typing import List, Optional, Tuple
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from app.db.models.document import Document, DocumentStatus
from app.db.models.document_page import DocumentPage
from app.db.models.document_relationship import DocumentRelationship, RelationshipType
from app.db.models.processing_job import ProcessingJob, JobStatus
from app.db.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db: Session):
        super().__init__(Document, db)

    def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[DocumentStatus] = None,
    ) -> Tuple[List[Document], int]:
        query = self.db.query(Document).filter(Document.user_id == user_id)
        if status:
            query = query.filter(Document.status == status)
        
        total = query.count()
        items = query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
        return items, total

    def get_by_id_and_user(self, document_id: str, user_id: str) -> Optional[Document]:
        return (
            self.db.query(Document)
            .filter(Document.id == document_id, Document.user_id == user_id)
            .first()
        )

    def get_by_hash_and_user(self, file_hash: str, user_id: str) -> Optional[Document]:
        return (
            self.db.query(Document)
            .filter(Document.file_hash == file_hash, Document.user_id == user_id)
            .first()
        )

    def create_page(self, page_data: dict) -> DocumentPage:
        page = DocumentPage(**page_data)
        self.db.add(page)
        self.db.commit()
        self.db.refresh(page)
        return page

    def get_pages(self, document_id: str) -> List[DocumentPage]:
        return (
            self.db.query(DocumentPage)
            .filter(DocumentPage.document_id == document_id)
            .order_by(DocumentPage.page_number)
            .all()
        )

    def create_job(self, document_id: str, celery_task_id: Optional[str] = None) -> ProcessingJob:
        job = ProcessingJob(
            document_id=document_id,
            celery_task_id=celery_task_id,
            status=JobStatus.QUEUED,
            current_stage="QUEUED",
            progress_percent=0,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_latest_job(self, document_id: str) -> Optional[ProcessingJob]:
        return (
            self.db.query(ProcessingJob)
            .filter(ProcessingJob.document_id == document_id)
            .order_by(desc(ProcessingJob.created_at))
            .first()
        )

    # Relationships
    def add_relationship(
        self,
        source_document_id: str,
        target_document_id: str,
        relationship_type: RelationshipType = RelationshipType.ANSWER_KEY,
    ) -> DocumentRelationship:
        rel = DocumentRelationship(
            source_document_id=source_document_id,
            target_document_id=target_document_id,
            relationship_type=relationship_type,
        )
        self.db.add(rel)
        self.db.commit()
        self.db.refresh(rel)
        return rel

    def get_relationships(self, document_id: str) -> List[DocumentRelationship]:
        return (
            self.db.query(DocumentRelationship)
            .filter(DocumentRelationship.source_document_id == document_id)
            .all()
        )

    def remove_relationship(self, source_document_id: str, target_document_id: str) -> bool:
        rel = (
            self.db.query(DocumentRelationship)
            .filter(
                DocumentRelationship.source_document_id == source_document_id,
                DocumentRelationship.target_document_id == target_document_id,
            )
            .first()
        )
        if rel:
            self.db.delete(rel)
            self.db.commit()
            return True
        return False
