from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.db.models.document_relationship import RelationshipType
from app.schemas.documents import DocumentListItem


class CreateRelationshipRequest(BaseModel):
    target_document_id: str = Field(..., description="ID of the document to associate")
    relationship_type: RelationshipType = Field(
        RelationshipType.ANSWER_KEY,
        description="Type of relationship (ANSWER_KEY, QUESTION_PAPER, SUPPLEMENT, etc.)",
    )


class RelationshipDetailResponse(BaseModel):
    id: str
    source_document_id: str
    target_document_id: str
    relationship_type: RelationshipType
    target_document: DocumentListItem
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentRelationshipsResponse(BaseModel):
    document_id: str
    total_relationships: int
    relationships: List[RelationshipDetailResponse]
