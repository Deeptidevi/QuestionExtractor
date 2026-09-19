from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundException, PermissionDeniedException, ConflictException
from app.db.models.document_relationship import DocumentRelationship, RelationshipType
from app.db.repositories.document_repo import DocumentRepository


class RelationshipService:
    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)

    def create_relationship(
        self,
        source_document_id: str,
        target_document_id: str,
        user_id: str,
        relationship_type: RelationshipType = RelationshipType.ANSWER_KEY,
    ) -> DocumentRelationship:
        # Validate both documents exist and belong to user
        src_doc = self.doc_repo.get(source_document_id)
        if not src_doc:
            raise ResourceNotFoundException("Source Document", source_document_id)
        if src_doc.user_id != user_id:
            raise PermissionDeniedException("You do not have permission for the source document.")

        tgt_doc = self.doc_repo.get(target_document_id)
        if not tgt_doc:
            raise ResourceNotFoundException("Target Document", target_document_id)
        if tgt_doc.user_id != user_id:
            raise PermissionDeniedException("You do not have permission for the target document.")

        if source_document_id == target_document_id:
            raise ConflictException("A document cannot be linked to itself.")

        # Check existing relationship
        existing = (
            self.db.query(DocumentRelationship)
            .filter(
                DocumentRelationship.source_document_id == source_document_id,
                DocumentRelationship.target_document_id == target_document_id,
                DocumentRelationship.relationship_type == relationship_type,
            )
            .first()
        )
        if existing:
            raise ConflictException("This document relationship already exists.")

        return self.doc_repo.add_relationship(
            source_document_id=source_document_id,
            target_document_id=target_document_id,
            relationship_type=relationship_type,
        )

    def list_relationships(self, document_id: str, user_id: str) -> List[DocumentRelationship]:
        src_doc = self.doc_repo.get(document_id)
        if not src_doc:
            raise ResourceNotFoundException("Document", document_id)
        if src_doc.user_id != user_id:
            raise PermissionDeniedException("You do not have permission for this document.")

        return self.doc_repo.get_relationships(document_id)

    def delete_relationship(
        self,
        source_document_id: str,
        target_document_id: str,
        user_id: str,
    ) -> bool:
        src_doc = self.doc_repo.get(source_document_id)
        if not src_doc or src_doc.user_id != user_id:
            raise PermissionDeniedException("You do not have permission for this operation.")

        deleted = self.doc_repo.remove_relationship(source_document_id, target_document_id)
        if not deleted:
            raise ResourceNotFoundException(
                "DocumentRelationship",
                f"{source_document_id} -> {target_document_id}",
            )
        return True
