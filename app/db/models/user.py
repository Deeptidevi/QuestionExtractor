from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
