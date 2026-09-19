import enum
from sqlalchemy import Column, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class RelationshipType(str, enum.Enum):
    ANSWER_KEY = "ANSWER_KEY"
    QUESTION_PAPER = "QUESTION_PAPER"
    SUPPLEMENT = "SUPPLEMENT"
    PART = "PART"
    REVISION = "REVISION"


class DocumentRelationship(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "document_relationships"

    source_document_id = Column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_document_id = Column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type = Column(
        Enum(RelationshipType),
        default=RelationshipType.ANSWER_KEY,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "source_document_id",
            "target_document_id",
            "relationship_type",
            name="uq_doc_relationship",
        ),
    )

    # Relationships
    source_document = relationship(
        "Document",
        foreign_keys=[source_document_id],
        back_populates="outgoing_relationships",
    )
    target_document = relationship(
        "Document",
        foreign_keys=[target_document_id],
        back_populates="incoming_relationships",
    )
