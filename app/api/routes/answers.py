from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.answer import AnswerMatchStatus
from app.services.answer_service import AnswerService
from app.schemas.answers import (
    DocumentAnswersResponse,
    AnswerDetailResponse,
)

router = APIRouter(prefix="/documents", tags=["Answers"])


@router.get("/{document_id}/answers", response_model=DocumentAnswersResponse)
def get_document_answers(
    document_id: str = Path(..., description="Document ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all detected answer keys, associated question IDs, and match confidence for a document.
    """
    service = AnswerService(db)
    answers = service.get_document_answers(document_id, current_user.id)

    matched = sum(1 for a in answers if a.match_status == AnswerMatchStatus.EXACT_MATCH and a.question_id is not None)
    unmatched = len(answers) - matched

    return DocumentAnswersResponse(
        document_id=document_id,
        total_answers=len(answers),
        matched_answers_count=matched,
        unmatched_answers_count=unmatched,
        answers=[
            AnswerDetailResponse(
                id=a.id,
                document_id=a.document_id,
                question_id=a.question_id,
                question_number=a.question_number,
                answer_value=a.answer_value,
                raw_answer_text=a.raw_answer_text,
                explanation=a.explanation,
                confidence=a.confidence,
                source_page=a.source_page,
                match_status=a.match_status,
                created_at=a.created_at,
            )
            for a in answers
        ],
    )
