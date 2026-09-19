from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.review_item import ReviewItem, ReviewSeverity
from app.db.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[ReviewItem]):
    def __init__(self, db: Session):
        super().__init__(ReviewItem, db)

    def get_by_document(
        self,
        document_id: str,
        unresolved_only: bool = False,
        severity: Optional[ReviewSeverity] = None,
    ) -> List[ReviewItem]:
        query = self.db.query(ReviewItem).filter(ReviewItem.document_id == document_id)
        if unresolved_only:
            query = query.filter(ReviewItem.is_resolved.is_(False))
        if severity:
            query = query.filter(ReviewItem.severity == severity)
        return query.order_by(ReviewItem.source_page, ReviewItem.created_at).all()

    def clear_document_reviews(self, document_id: str) -> int:
        deleted_count = (
            self.db.query(ReviewItem)
            .filter(ReviewItem.document_id == document_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted_count
