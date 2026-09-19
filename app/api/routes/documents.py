import math
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.document import DocumentStatus
from app.services.document_service import DocumentService
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.schemas.documents import (
    DocumentUploadResponse,
    DocumentStatusResponse,
    DocumentDetailResponse,
    DocumentListItem,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(..., description="PDF or image file (JPG, JPEG, PNG)"),
    title: Optional[str] = Form(None, description="Optional custom document title"),
    sync_process: bool = Form(False, description="Set True for direct synchronous processing (e.g. testing)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a PDF or Image file for asynchronous extraction.
    Returns immediately with document_id and QUEUED status.
    """
    service = DocumentService(db)
    
    # Read file contents and length
    file_bytes = await file.read()
    file_size = len(file_bytes)
    
    import io
    file_stream = io.BytesIO(file_bytes)

    doc, job = service.upload_document(
        file_obj=file_stream,
        filename=file.filename or "uploaded_document",
        content_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        user_id=current_user.id,
        title=title,
        sync_process=sync_process,
    )

    return DocumentUploadResponse(
        document_id=doc.id,
        title=doc.title,
        original_filename=doc.original_filename,
        status=doc.status,
        message="Document uploaded successfully and queued for asynchronous processing"
    )


@router.get("", response_model=PaginatedResponse[DocumentListItem])
def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    status: Optional[DocumentStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List user's uploaded documents with pagination and status filters.
    """
    service = DocumentService(db)
    skip = (page - 1) * page_size
    items, total = service.list_documents(
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
        status=status,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse[DocumentListItem](
        items=items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        ),
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document_details(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve document details, page breakdown, and metadata.
    """
    service = DocumentService(db)
    doc = service.get_document(document_id, current_user.id)
    return doc


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Track processing status, job progress percent, and error details.
    """
    service = DocumentService(db)
    return service.get_document_status(document_id, current_user.id)


@router.delete("/{document_id}", response_model=SuccessResponse)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a document and all its extracted artifacts from storage and database.
    """
    service = DocumentService(db)
    service.delete_document(document_id, current_user.id)
    return SuccessResponse(message=f"Document '{document_id}' deleted successfully.")
