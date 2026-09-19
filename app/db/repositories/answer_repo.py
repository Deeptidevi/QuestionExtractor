from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.answer import Answer, AnswerMatchStatus
from app.db.repositories.base import BaseRepository


class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, db: Session):
        super().__init__(Answer, db)

    def get_by_document(self, document_id: str) -> List[Answer]:
        return (
            self.db.query(Answer)
            .filter(Answer.document_id == document_id)
            .order_by(Answer.source_page, Answer.question_number)
            .all()
        )

    def get_by_question(self, question_id: str) -> Optional[Answer]:
        return self.db.query(Answer).filter(Answer.question_id == question_id).first()

    def clear_document_answers(self, document_id: str) -> int:
        deleted_count = (
            self.db.query(Answer)
            .filter(Answer.document_id == document_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted_count
