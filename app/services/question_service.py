from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundException, PermissionDeniedException
from app.db.models.document import Document
from app.db.models.question import Question, QuestionType
from app.db.models.answer import Answer
from app.db.repositories.question_repo import QuestionRepository
from app.db.repositories.document_repo import DocumentRepository


class QuestionService:
    def __init__(self, db: Session):
        self.db = db
        self.question_repo = QuestionRepository(db)
        self.document_repo = DocumentRepository(db)

    def list_questions(
        self,
        document_id: str,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        question_type: Optional[QuestionType] = None,
        review_required: Optional[bool] = None,
    ) -> Tuple[List[Question], int]:
        # Validate document ownership
        doc = self.document_repo.get(document_id)
        if not doc:
            raise ResourceNotFoundException("Document", document_id)
        if doc.user_id != user_id:
            raise PermissionDeniedException("You do not have access to this document's questions.")

        return self.question_repo.get_by_document(
            document_id=document_id,
            skip=skip,
            limit=limit,
            question_type=question_type,
            review_required=review_required,
        )

    def get_question(self, question_id: str, user_id: str) -> Question:
        question = self.question_repo.get_with_details(question_id)
        if not question:
            raise ResourceNotFoundException("Question", question_id)

        # Validate ownership via parent document
        doc = self.document_repo.get(question.document_id)
        if not doc or doc.user_id != user_id:
            raise PermissionDeniedException("You do not have access to this question.")

        return question
