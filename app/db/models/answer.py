import enum
from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class AnswerMatchStatus(str, enum.Enum):
    EXACT_MATCH = "EXACT_MATCH"
    INFERRED = "INFERRED"
    AMBIGUOUS = "AMBIGUOUS"
    UNMATCHED = "UNMATCHED"


class Answer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "answers"

    document_id = Column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        String(36),
        ForeignKey("questions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    question_number = Column(String(50), nullable=True, index=True)
    answer_value = Column(String(255), nullable=True)  # e.g., 'C' or 'True' or 'Photosynthesis'
    raw_answer_text = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)
    source_page = Column(Integer, nullable=True)
    match_status = Column(
        Enum(AnswerMatchStatus),
        default=AnswerMatchStatus.EXACT_MATCH,
        nullable=False,
        index=True,
    )

    # Relationships
    document = relationship("Document", back_populates="answers")
    question = relationship("Question", back_populates="answers")
