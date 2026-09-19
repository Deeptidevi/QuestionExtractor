from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from app.db.models.question import QuestionType, ExtractionStatus
from app.db.models.question_asset import AssetType


class OptionDetail(BaseModel):
    id: Optional[str] = None
    label: str = Field(..., description="Option identifier (A, B, C, etc.)")
    option_text: str = Field(..., description="The option's textual content")
    position: int = 1
    is_correct: Optional[bool] = None
    confidence: float = 1.0

    model_config = ConfigDict(from_attributes=True)


class AssetDetail(BaseModel):
    id: Optional[str] = None
    asset_type: AssetType
    storage_path: str
    source_page: int
    bbox: List[float] = []
    caption: Optional[str] = None
    confidence: float = 1.0

    model_config = ConfigDict(from_attributes=True)


class QuestionAnswerSummary(BaseModel):
    id: Optional[str] = None
    answer_value: Optional[str] = None
    raw_answer_text: Optional[str] = None
    confidence: float = 1.0
    source_page: Optional[int] = None
    match_status: str

    model_config = ConfigDict(from_attributes=True)


class QuestionDetailResponse(BaseModel):
    id: str
    document_id: str
    question_number: Optional[str]
    sequence_order: int
    question_text: str
    raw_text: str
    question_type: QuestionType
    options: List[OptionDetail] = []
    assets: List[AssetDetail] = []
    answer: Optional[QuestionAnswerSummary] = None
    source_pages: List[int] = []
    source_regions: List[Dict[str, Any]] = []
    extraction_confidence: float
    extraction_status: ExtractionStatus
    review_required: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionListItem(BaseModel):
    id: str
    document_id: str
    question_number: Optional[str]
    sequence_order: int
    question_text: str
    question_type: QuestionType
    options_count: int
    has_answer: bool
    answer_value: Optional[str] = None
    source_pages: List[int] = []
    extraction_confidence: float
    extraction_status: ExtractionStatus
    review_required: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
