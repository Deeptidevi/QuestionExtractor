import enum
from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class AssetType(str, enum.Enum):
    IMAGE = "IMAGE"
    TABLE = "TABLE"
    DIAGRAM = "DIAGRAM"
    FORMULA = "FORMULA"


class QuestionAsset(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "question_assets"

    question_id = Column(
        String(36),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    asset_type = Column(
        Enum(AssetType),
        default=AssetType.IMAGE,
        nullable=False,
    )
    storage_path = Column(String(512), nullable=False)
    source_page = Column(Integer, nullable=False)
    bbox = Column(JSON, default=list, nullable=False)  # [x0, y0, x1, y1]
    caption = Column(String(500), nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)

    # Relationships
    question = relationship("Question", back_populates="assets")
