import enum
from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class WarningType(str, enum.Enum):
    LOW_OCR_CONFIDENCE = "LOW_OCR_CONFIDENCE"
    QUESTION_NUMBER_UNCERTAIN = "QUESTION_NUMBER_UNCERTAIN"
    QUESTION_BOUNDARY_UNCERTAIN = "QUESTION_BOUNDARY_UNCERTAIN"
    QUESTION_CONTINUES_NEXT_PAGE = "QUESTION_CONTINUES_NEXT_PAGE"
    MISSING_QUESTION_NUMBER = "MISSING_QUESTION_NUMBER"
    OPTIONS_UNCERTAIN = "OPTIONS_UNCERTAIN"
    IMAGE_ASSOCIATION_UNCERTAIN = "IMAGE_ASSOCIATION_UNCERTAIN"
    TABLE_ASSOCIATION_UNCERTAIN = "TABLE_ASSOCIATION_UNCERTAIN"
    ANSWER_NOT_FOUND = "ANSWER_NOT_FOUND"
    ANSWER_MATCH_UNCERTAIN = "ANSWER_MATCH_UNCERTAIN"
    OCR_ERROR = "OCR_ERROR"
    UNSUPPORTED_LAYOUT = "UNSUPPORTED_LAYOUT"
    PARTIAL_EXTRACTION = "PARTIAL_EXTRACTION"


class ReviewSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class ReviewItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "review_items"

    document_id = Column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        String(36),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    warning_type = Column(
        Enum(WarningType),
        nullable=False,
        index=True,
    )
    severity = Column(
        Enum(ReviewSeverity),
        default=ReviewSeverity.WARNING,
        nullable=False,
    )
    message = Column(Text, nullable=False)
    source_page = Column(Integer, nullable=True)
    confidence = Column(Float, nullable=True)
    details = Column(JSON, default=dict, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    document = relationship("Document", back_populates="review_items")
    question = relationship("Question", back_populates="review_items")
