from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class QuestionOption(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "question_options"

    question_id = Column(
        String(36),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label = Column(String(20), nullable=False)  # e.g., 'A', 'B', 'C', '1', 'a'
    option_text = Column(Text, nullable=False)
    position = Column(Integer, nullable=False, default=1)
    is_correct = Column(Boolean, nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)

    # Relationships
    question = relationship("Question", back_populates="options")
