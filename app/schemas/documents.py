from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from app.db.models.document import DocumentStatus
from app.db.models.processing_job import JobStatus


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Unique document ID")
    title: str
    original_filename: str
    status: DocumentStatus
    message: str = "Document uploaded successfully and queued for asynchronous processing"


class DocumentStatusResponse(BaseModel):
    document_id: str
    status: DocumentStatus
    total_pages: int
    is_scanned: bool
    overall_confidence: Optional[float]
    current_job_id: Optional[str] = None
    job_status: Optional[JobStatus] = None
    current_stage: Optional[str] = None
    progress_percent: Optional[int] = None
    error_summary: Optional[str] = None
    review_required_count: int = 0
    total_questions: int = 0
    updated_at: datetime


class DocumentPageSummary(BaseModel):
    id: str
    page_number: int
    char_count: int
    word_count: int
    ocr_applied: bool
    ocr_confidence: Optional[float]
    width: Optional[float]
    height: Optional[float]
    rotation: int

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(BaseModel):
    id: str
    user_id: str
    title: str
    original_filename: str
    mime_type: str
    file_size: int
    total_pages: int
    is_scanned: bool
    status: DocumentStatus
    overall_confidence: Optional[float]
    created_at: datetime
    updated_at: datetime
    pages: List[DocumentPageSummary] = []

    model_config = ConfigDict(from_attributes=True)


class DocumentListItem(BaseModel):
    id: str
    title: str
    original_filename: str
    mime_type: str
    file_size: int
    total_pages: int
    is_scanned: bool
    status: DocumentStatus
    overall_confidence: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
