from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from app.db.models.review_item import WarningType, ReviewSeverity


class ReviewItemResponse(BaseModel):
    id: str
    document_id: str
    question_id: Optional[str]
    warning_type: WarningType
    severity: ReviewSeverity
    message: str
    source_page: Optional[int]
    confidence: Optional[float]
    details: Dict[str, Any] = {}
    is_resolved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentReviewSummaryResponse(BaseModel):
    document_id: str
    total_review_items: int
    unresolved_items: int
    critical_count: int
    warning_count: int
    info_count: int
    items: List[ReviewItemResponse]


class ResolveReviewItemRequest(BaseModel):
    is_resolved: bool = True
    resolution_note: Optional[str] = None
