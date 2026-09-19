import math
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.question import QuestionType
from app.services.question_service import QuestionService
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.questions import (
    QuestionDetailResponse,
    QuestionListItem,
    QuestionAnswerSummary,
    OptionDetail,
    AssetDetail,
)

router = APIRouter(tags=["Questions"])


@router.get("/documents/{document_id}/questions", response_model=PaginatedResponse[QuestionListItem])
def list_document_questions(
    document_id: str = Path(..., description="Document ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    question_type: Optional[QuestionType] = Query(None, description="Filter by question type"),
    review_required: Optional[bool] = Query(None, description="Filter by review required"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve extracted structured questions for a document with pagination and filters.
    """
    service = QuestionService(db)
    skip = (page - 1) * page_size
    items, total = service.list_questions(
        document_id=document_id,
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
        question_type=question_type,
        review_required=review_required,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    question_items = []
    for q in items:
        # Check if matched answer exists
        ans = q.answers[0] if q.answers else None
        question_items.append(
            QuestionListItem(
                id=q.id,
                document_id=q.document_id,
                question_number=q.question_number,
                sequence_order=q.sequence_order,
                question_text=q.question_text,
                question_type=q.question_type,
                options_count=len(q.options),
                has_answer=ans is not None,
                answer_value=ans.answer_value if ans else None,
                source_pages=q.source_pages,
                extraction_confidence=q.extraction_confidence,
                extraction_status=q.extraction_status,
                review_required=q.review_required,
                created_at=q.created_at,
            )
        )

    return PaginatedResponse[QuestionListItem](
        items=question_items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        ),
    )


@router.get("/questions/{question_id}", response_model=QuestionDetailResponse)
def get_question_detail(
    question_id: str = Path(..., description="Question ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve an individual question with full options, assets, source regions, and answers.
    """
    service = QuestionService(db)
    q = service.get_question(question_id=question_id, user_id=current_user.id)
    
    ans = q.answers[0] if q.answers else None
    ans_summary = None
    if ans:
        ans_summary = QuestionAnswerSummary(
            id=ans.id,
            answer_value=ans.answer_value,
            raw_answer_text=ans.raw_answer_text,
            confidence=ans.confidence,
            source_page=ans.source_page,
            match_status=ans.match_status.value,
        )

    return QuestionDetailResponse(
        id=q.id,
        document_id=q.document_id,
        question_number=q.question_number,
        sequence_order=q.sequence_order,
        question_text=q.question_text,
        raw_text=q.raw_text,
        question_type=q.question_type,
        options=[
            OptionDetail(
                id=opt.id,
                label=opt.label,
                option_text=opt.option_text,
                position=opt.position,
                is_correct=opt.is_correct,
                confidence=opt.confidence,
            )
            for opt in q.options
        ],
        assets=[
            AssetDetail(
                id=ast.id,
                asset_type=ast.asset_type,
                storage_path=ast.storage_path,
                source_page=ast.source_page,
                bbox=ast.bbox or [],
                caption=ast.caption,
                confidence=ast.confidence,
            )
            for ast in q.assets
        ],
        answer=ans_summary,
        source_pages=q.source_pages or [],
        source_regions=q.source_regions or [],
        extraction_confidence=q.extraction_confidence,
        extraction_status=q.extraction_status,
        review_required=q.review_required,
        created_at=q.created_at,
        updated_at=q.updated_at,
    )
