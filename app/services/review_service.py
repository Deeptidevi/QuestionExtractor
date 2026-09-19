from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundException, PermissionDeniedException
from app.db.models.review_item import ReviewItem, ReviewSeverity
from app.db.repositories.review_repo import ReviewRepository
from app.db.repositories.document_repo import DocumentRepository


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.document_repo = DocumentRepository(db)

    def get_document_review_summary(
        self,
        document_id: str,
        user_id: str,
        unresolved_only: bool = False,
        severity: Optional[ReviewSeverity] = None,
    ) -> dict:
        doc = self.document_repo.get(document_id)
        if not doc:
            raise ResourceNotFoundException("Document", document_id)
        if doc.user_id != user_id:
            raise PermissionDeniedException("You do not have access to this document's review items.")

        items = self.review_repo.get_by_document(
            document_id=document_id,
            unresolved_only=unresolved_only,
            severity=severity,
        )

        unresolved = sum(1 for item in items if not item.is_resolved)
        critical_count = sum(1 for item in items if item.severity == ReviewSeverity.CRITICAL)
        warning_count = sum(1 for item in items if item.severity == ReviewSeverity.WARNING)
        info_count = sum(1 for item in items if item.severity == ReviewSeverity.INFO)

        return {
            "document_id": document_id,
            "total_review_items": len(items),
            "unresolved_items": unresolved,
            "critical_count": critical_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "items": items,
        }

    def resolve_review_item(
        self,
        review_item_id: str,
        user_id: str,
        is_resolved: bool = True,
        note: Optional[str] = None,
    ) -> ReviewItem:
        item = self.review_repo.get(review_item_id)
        if not item:
            raise ResourceNotFoundException("ReviewItem", review_item_id)

        doc = self.document_repo.get(item.document_id)
        if not doc or doc.user_id != user_id:
            raise PermissionDeniedException("You do not have permission to modify this review item.")

        update_data = {"is_resolved": is_resolved}
        if note:
            details = dict(item.details)
            details["resolution_note"] = note
            update_data["details"] = details

        return self.review_repo.update(item, update_data)
