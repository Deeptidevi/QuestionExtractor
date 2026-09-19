from typing import List, Optional, Tuple
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.db.models.question import Question, QuestionType, ExtractionStatus
from app.db.models.question_option import QuestionOption
from app.db.models.question_asset import QuestionAsset
from app.db.repositories.base import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, db: Session):
        super().__init__(Question, db)

    def get_by_document(
        self,
        document_id: str,
        skip: int = 0,
        limit: int = 50,
        question_type: Optional[QuestionType] = None,
        review_required: Optional[bool] = None,
    ) -> Tuple[List[Question], int]:
        query = self.db.query(Question).filter(Question.document_id == document_id)
        
        if question_type:
            query = query.filter(Question.question_type == question_type)
        if review_required is not None:
            query = query.filter(Question.review_required == review_required)

        total = query.count()
        items = query.order_by(Question.sequence_order).offset(skip).limit(limit).all()
        return items, total

    def get_with_details(self, question_id: str) -> Optional[Question]:
        return self.db.query(Question).filter(Question.id == question_id).first()

    def create_option(self, option_data: dict) -> QuestionOption:
        opt = QuestionOption(**option_data)
        self.db.add(opt)
        self.db.commit()
        self.db.refresh(opt)
        return opt

    def create_asset(self, asset_data: dict) -> QuestionAsset:
        asset = QuestionAsset(**asset_data)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def clear_document_questions(self, document_id: str) -> int:
        """Idempotency helper: remove previous extracted questions before re-processing."""
        deleted_count = (
            self.db.query(Question)
            .filter(Question.document_id == document_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted_count
