import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_base, declared_attr

Base = declarative_base()


class TimestampMixin:
    """Provides standard UTC timestamp columns for all models."""
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Provides a consistent UUID string primary key across PostgreSQL and SQLite."""
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        nullable=False,
    )
