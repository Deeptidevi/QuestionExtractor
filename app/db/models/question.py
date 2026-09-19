import enum
from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    TRUE_FALSE = "TRUE_FALSE"
    SHORT_ANSWER = "SHORT_ANSWER"
    LONG_ANSWER = "LONG_ANSWER"
    FILL_IN_THE_BLANK = "FILL_IN_THE_BLANK"
    MATCHING = "MATCHING"
    UNKNOWN = "UNKNOWN"


class ExtractionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FAILED = "FAILED"


class Question(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "questions"

    document_id = Column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    question_number = Column(String(50), nullable=True, index=True)
    sequence_order = Column(Integer, nullable=False, default=1)
    
    raw_text = Column(Text, nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(
        Enum(QuestionType),
        default=QuestionType.MCQ,
        nullable=False,
        index=True,
    )
    
    # Source page traceability
    source_pages = Column(JSON, default=list, nullable=False)  # e.g. [1, 2]
    source_regions = Column(JSON, default=list, nullable=False) # list of bounding boxes
    
    # Confidence metrics
    extraction_confidence = Column(Float, default=1.0, nullable=False)
    extraction_status = Column(
        Enum(ExtractionStatus),
        default=ExtractionStatus.SUCCESS,
        nullable=False,
        index=True,
    )
    review_required = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    document = relationship("Document", back_populates="questions")
    options = relationship(
        "QuestionOption",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOption.position",
    )
    assets = relationship(
        "QuestionAsset",
        back_populates="question",
        cascade="all, delete-orphan",
    )
    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
    )
    review_items = relationship(
        "ReviewItem",
        back_populates="question",
        cascade="all, delete-orphan",
    )
