from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.services.relationship_service import RelationshipService
from app.schemas.common import SuccessResponse
from app.schemas.documents import DocumentListItem
from app.schemas.relationships import (
    CreateRelationshipRequest,
    RelationshipDetailResponse,
    DocumentRelationshipsResponse,
)

router = APIRouter(prefix="/documents", tags=["Document Relationships"])


@router.post(
    "/{document_id}/relationships",
    response_model=RelationshipDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document_relationship(
    document_id: str = Path(..., description="Source Document ID (e.g. Question Paper)"),
    request: CreateRelationshipRequest = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Associate related documents (e.g. linking a Question Paper with its separate Answer Key document).
    """
    service = RelationshipService(db)
    rel = service.create_relationship(
        source_document_id=document_id,
        target_document_id=request.target_document_id,
        user_id=current_user.id,
        relationship_type=request.relationship_type,
    )

    tgt = rel.target_document
    return RelationshipDetailResponse(
        id=rel.id,
        source_document_id=rel.source_document_id,
        target_document_id=rel.target_document_id,
        relationship_type=rel.relationship_type,
        target_document=DocumentListItem(
            id=tgt.id,
            title=tgt.title,
            original_filename=tgt.original_filename,
            mime_type=tgt.mime_type,
            file_size=tgt.file_size,
            total_pages=tgt.total_pages,
            is_scanned=tgt.is_scanned,
            status=tgt.status,
            overall_confidence=tgt.overall_confidence,
            created_at=tgt.created_at,
            updated_at=tgt.updated_at,
        ),
        created_at=rel.created_at,
    )


@router.get("/{document_id}/relationships", response_model=DocumentRelationshipsResponse)
def list_document_relationships(
    document_id: str = Path(..., description="Source Document ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all linked relationships for a document.
    """
    service = RelationshipService(db)
    relationships = service.list_relationships(document_id, current_user.id)

    res_items = []
    for rel in relationships:
        tgt = rel.target_document
        res_items.append(
            RelationshipDetailResponse(
                id=rel.id,
                source_document_id=rel.source_document_id,
                target_document_id=rel.target_document_id,
                relationship_type=rel.relationship_type,
                target_document=DocumentListItem(
                    id=tgt.id,
                    title=tgt.title,
                    original_filename=tgt.original_filename,
                    mime_type=tgt.mime_type,
                    file_size=tgt.file_size,
                    total_pages=tgt.total_pages,
                    is_scanned=tgt.is_scanned,
                    status=tgt.status,
                    overall_confidence=tgt.overall_confidence,
                    created_at=tgt.created_at,
                    updated_at=tgt.updated_at,
                ),
                created_at=rel.created_at,
            )
        )

    return DocumentRelationshipsResponse(
        document_id=document_id,
        total_relationships=len(res_items),
        relationships=res_items,
    )


@router.delete("/{document_id}/relationships/{related_document_id}", response_model=SuccessResponse)
def delete_document_relationship(
    document_id: str = Path(..., description="Source Document ID"),
    related_document_id: str = Path(..., description="Related Document ID to unlink"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Unlink an associated document relationship.
    """
    service = RelationshipService(db)
    service.delete_relationship(
        source_document_id=document_id,
        target_document_id=related_document_id,
        user_id=current_user.id,
    )
    return SuccessResponse(message="Document relationship removed successfully.")
