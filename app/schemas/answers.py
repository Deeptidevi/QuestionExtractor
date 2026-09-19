from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.db.models.answer import AnswerMatchStatus


class AnswerDetailResponse(BaseModel):
    id: str
    document_id: str
    question_id: Optional[str]
    question_number: Optional[str]
    answer_value: Optional[str]
    raw_answer_text: Optional[str]
    explanation: Optional[str]
    confidence: float
    source_page: Optional[int]
    match_status: AnswerMatchStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentAnswersResponse(BaseModel):
    document_id: str
    total_answers: int
    matched_answers_count: int
    unmatched_answers_count: int
    answers: List[AnswerDetailResponse]
