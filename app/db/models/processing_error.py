from sqlalchemy import Column, ForeignKey, JSON, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class ProcessingError(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "processing_errors"

    document_id = Column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id = Column(
        String(36),
        ForeignKey("processing_jobs.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    stage = Column(String(100), nullable=False, index=True)
    error_code = Column(String(100), nullable=False, index=True)
    error_message = Column(Text, nullable=False)
    traceback_details = Column(Text, nullable=True)
    error_metadata = Column(JSON, default=dict, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="errors")
