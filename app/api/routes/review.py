from typing import Optional
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.review_item import ReviewSeverity
from app.services.review_service import ReviewService
from app.schemas.review import (
    DocumentReviewSummaryResponse,
    ReviewItemResponse,
    ResolveReviewItemRequest,
)

router = APIRouter(tags=["Review & Warnings"])


@router.get("/documents/{document_id}/review-items", response_model=DocumentReviewSummaryResponse)
def get_document_review_items(
    document_id: str = Path(..., description="Document ID"),
    unresolved_only: bool = Query(False, description="Filter only unresolved items"),
    severity: Optional[ReviewSeverity] = Query(None, description="Filter by severity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve review items, warnings, and confidence flags for human reviewers.
    """
    service = ReviewService(db)
    summary = service.get_document_review_summary(
        document_id=document_id,
        user_id=current_user.id,
        unresolved_only=unresolved_only,
        severity=severity,
    )
    return summary


@router.post("/review-items/{review_item_id}/resolve", response_model=ReviewItemResponse)
def resolve_review_item(
    review_item_id: str = Path(..., description="Review Item ID"),
    request: ResolveReviewItemRequest = ResolveReviewItemRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a flagged review item as resolved with optional resolution notes.
    """
    service = ReviewService(db)
    item = service.resolve_review_item(
        review_item_id=review_item_id,
        user_id=current_user.id,
        is_resolved=request.is_resolved,
        note=request.resolution_note,
    )
    return item
