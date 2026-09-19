import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ProcessingJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "processing_jobs"

    document_id = Column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    celery_task_id = Column(String(255), nullable=True, index=True)
    status = Column(
        Enum(JobStatus),
        default=JobStatus.PENDING,
        nullable=False,
        index=True,
    )
    current_stage = Column(String(100), nullable=True)
    progress_percent = Column(Integer, default=0, nullable=False)
    
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    
    error_summary = Column(Text, nullable=True)
    job_metadata = Column(JSON, default=dict, nullable=False)

    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="jobs")
