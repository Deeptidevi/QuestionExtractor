import os
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # App Info
    APP_NAME: str = "Document Processing & Question Extraction Service"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = "dev_insecure_secret_key_change_in_production_minimum_32_characters_long_12345"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"

    # CORS
    FRONTEND_URL: str = ""
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "doc_processing_db"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/doc_processing_db"

    # Redis & Celery
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    # Storage
    STORAGE_BACKEND: str = "local"  # 'local' or 's3'
    LOCAL_STORAGE_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/jpg",
    ]

    # S3 Object Storage (for Production / Render / AWS / MinIO)
    S3_ENDPOINT: str = ""
    S3_BUCKET: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_REGION: str = "us-east-1"

    # OCR Settings
    OCR_PROVIDER: str = "tesseract"  # 'tesseract', 'mock', 'external'
    TESSERACT_CMD: str = "tesseract"
    OCR_FALLBACK_CONFIDENCE_THRESHOLD: float = 0.60
    OCR_PAGE_DENSITY_THRESHOLD: int = 50  # Characters per page

    # Question Extraction & Confidence
    EXTRACTION_ENGINE: str = "rule_based"  # 'rule_based', 'ai', 'hybrid'
    CONFIDENCE_HIGH_THRESHOLD: float = 0.85
    CONFIDENCE_MEDIUM_THRESHOLD: float = 0.60
    CONFIDENCE_REVIEW_THRESHOLD: float = 0.60

    # External AI (Optional/Pluggable)
    AI_PROVIDER_ENABLED: bool = False
    AI_PROVIDER_NAME: str = "gemini"
    AI_API_KEY: str = ""
    AI_MODEL_NAME: str = "gemini-1.5-flash"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: str) -> str:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg2://", 1)
        elif v and v.startswith("postgresql://") and not v.startswith("postgresql+"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def assemble_celery_broker(cls, v: str, info) -> str:
        if v:
            return v
        data = info.data if hasattr(info, "data") else {}
        return data.get("REDIS_URL", "redis://localhost:6379/0")

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def assemble_celery_backend(cls, v: str, info) -> str:
        if v:
            return v
        data = info.data if hasattr(info, "data") else {}
        return data.get("REDIS_URL", "redis://localhost:6379/0")

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, str) and v.startswith("["):
            import json
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.strip("[]").split(",") if i.strip()]
        return v

    @field_validator("ALLOWED_MIME_TYPES", mode="before")
    @classmethod
    def assemble_mime_types(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        return v


settings = Settings()
