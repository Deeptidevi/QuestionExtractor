from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundException, PermissionDeniedException
from app.db.models.answer import Answer
from app.db.repositories.answer_repo import AnswerRepository
from app.db.repositories.document_repo import DocumentRepository


class AnswerService:
    def __init__(self, db: Session):
        self.db = db
        self.answer_repo = AnswerRepository(db)
        self.document_repo = DocumentRepository(db)

    def get_document_answers(self, document_id: str, user_id: str) -> List[Answer]:
        doc = self.document_repo.get(document_id)
        if not doc:
            raise ResourceNotFoundException("Document", document_id)
        if doc.user_id != user_id:
            raise PermissionDeniedException("You do not have access to this document's answers.")

        return self.answer_repo.get_by_document(document_id)

    def get_answer_for_question(self, question_id: str, user_id: str) -> Optional[Answer]:
        return self.answer_repo.get_by_question(question_id)
