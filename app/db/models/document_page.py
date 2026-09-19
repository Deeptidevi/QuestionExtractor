from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class DocumentPage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "document_pages"

    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False, index=True)
    raw_text = Column(Text, nullable=True)
    cleaned_text = Column(Text, nullable=True)
    
    # Page layout metadata
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    rotation = Column(Integer, default=0, nullable=False)
    
    # Extraction flags & stats
    char_count = Column(Integer, default=0, nullable=False)
    word_count = Column(Integer, default=0, nullable=False)
    ocr_applied = Column(Boolean, default=False, nullable=False)
    ocr_confidence = Column(Float, nullable=True)
    
    # Structured blocks / tables / layout bounding boxes (JSON)
    extracted_blocks = Column(JSON, default=list, nullable=False)
    extracted_tables = Column(JSON, default=list, nullable=False)
    extracted_images = Column(JSON, default=list, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="pages")
