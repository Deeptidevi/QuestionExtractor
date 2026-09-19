import enum
from sqlalchemy import BigInteger, Boolean, Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class DocumentStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    FAILED = "FAILED"


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "documents"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_path = Column(String(512), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256 for integrity & deduplication
    
    total_pages = Column(Integer, default=0, nullable=False)
    is_scanned = Column(Boolean, default=False, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False, index=True)
    overall_confidence = Column(Float, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="documents")
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan", order_by="DocumentPage.page_number")
    jobs = relationship("ProcessingJob", back_populates="document", cascade="all, delete-orphan", order_by="desc(ProcessingJob.created_at)")
    questions = relationship("Question", back_populates="document", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="document", cascade="all, delete-orphan")
    review_items = relationship("ReviewItem", back_populates="document", cascade="all, delete-orphan")
    errors = relationship("ProcessingError", back_populates="document", cascade="all, delete-orphan")

    # Related documents
    outgoing_relationships = relationship(
        "DocumentRelationship",
        foreign_keys="DocumentRelationship.source_document_id",
        back_populates="source_document",
        cascade="all, delete-orphan",
    )
    incoming_relationships = relationship(
        "DocumentRelationship",
        foreign_keys="DocumentRelationship.target_document_id",
        back_populates="target_document",
        cascade="all, delete-orphan",
    )
