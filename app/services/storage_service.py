import abc
import hashlib
import os
import shutil
import uuid
from pathlib import Path
from typing import BinaryIO, Optional, Tuple
from app.core.config import settings
from app.core.exceptions import InvalidFileException, FileTooLargeException, UnsupportedFileTypeException
from app.core.logging import logger


class BaseStorageService(abc.ABC):
    """Abstract interface for file storage (Local disk, S3, GCS, MinIO, etc.)."""

    @abc.abstractmethod
    def save_file(
        self,
        file_obj: BinaryIO,
        original_filename: str,
        content_type: str,
        subfolder: str = "documents",
    ) -> Tuple[str, str, int]:
        """
        Saves a file stream to storage.
        Returns (stored_relative_path, sha256_hash, file_size_bytes).
        """
        pass

    @abc.abstractmethod
    def get_file_path(self, relative_path: str) -> str:
        """Resolves the physical or URI path of the stored file."""
        pass

    @abc.abstractmethod
    def delete_file(self, relative_path: str) -> bool:
        """Deletes a file from storage."""
        pass

    @abc.abstractmethod
    def file_exists(self, relative_path: str) -> bool:
        """Checks if a file exists in storage."""
        pass


class LocalStorageService(BaseStorageService):
    """
    Local filesystem storage with path traversal protection,
    SHA-256 hash calculation, size checks, and UUID-prefixed file names.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.LOCAL_STORAGE_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @property
    def base_path(self) -> Path:
        p = Path(self.base_dir).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _sanitize_filename(self, filename: str) -> str:
        clean_name = os.path.basename(filename).strip().replace(" ", "_")
        return clean_name or "uploaded_file"

    def _safe_resolve(self, relative_path: str) -> Path:
        resolved = (self.base_path / relative_path).resolve()
        if not str(resolved).startswith(str(self.base_path)):
            raise InvalidFileException("Path traversal attempt detected.")
        return resolved

    def save_file(
        self,
        file_obj: BinaryIO,
        original_filename: str,
        content_type: str,
        subfolder: str = "documents",
    ) -> Tuple[str, str, int]:
        clean_filename = self._sanitize_filename(original_filename)
        unique_name = f"{uuid.uuid4().hex}_{clean_filename}"
        
        target_dir = self.base_path / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = target_dir / unique_name
        hasher = hashlib.sha256()
        total_bytes = 0

        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        with open(target_path, "wb") as dest:
            while chunk := file_obj.read(1024 * 64):  # 64 KB chunks
                total_bytes += len(chunk)
                if total_bytes > settings.MAX_UPLOAD_SIZE_BYTES:
                    dest.close()
                    if target_path.exists():
                        target_path.unlink()
                    raise FileTooLargeException(
                        max_bytes=settings.MAX_UPLOAD_SIZE_BYTES,
                        actual_bytes=total_bytes,
                    )
                hasher.update(chunk)
                dest.write(chunk)

        sha256_hash = hasher.hexdigest()
        relative_path = os.path.relpath(target_path, self.base_path).replace("\\", "/")
        
        logger.info(
            f"Stored file '{original_filename}' as '{relative_path}' ({total_bytes} bytes, hash={sha256_hash[:8]}...)"
        )
        return relative_path, sha256_hash, total_bytes

    def get_file_path(self, relative_path: str) -> str:
        safe_path = self._safe_resolve(relative_path)
        return str(safe_path)

    def delete_file(self, relative_path: str) -> bool:
        try:
            safe_path = self._safe_resolve(relative_path)
            if safe_path.exists() and safe_path.is_file():
                safe_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file '{relative_path}': {e}")
            return False

    def file_exists(self, relative_path: str) -> bool:
        try:
            safe_path = self._safe_resolve(relative_path)
            return safe_path.exists() and safe_path.is_file()
        except Exception:
            return False


class S3CompatibleStorageService(BaseStorageService):
    """
    S3-compatible object storage provider (AWS S3, Cloudflare R2, MinIO, Wasabi, Render Disks/Buckets).
    Downloads files temporarily to a local cache directory for OCR/PyMuPDF processing when needed.
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region_name: Optional[str] = None,
        cache_dir: Optional[str] = None,
    ):
        self.bucket_name = bucket_name or settings.S3_BUCKET
        self.endpoint_url = endpoint_url or settings.S3_ENDPOINT or None
        self.access_key = access_key or settings.S3_ACCESS_KEY
        self.secret_key = secret_key or settings.S3_SECRET_KEY
        self.region_name = region_name or settings.S3_REGION or "us-east-1"
        self.cache_dir = Path(cache_dir or "./data/cache").resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import boto3
                from botocore.config import Config

                self._client = boto3.client(
                    "s3",
                    endpoint_url=self.endpoint_url,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region_name,
                    config=Config(signature_version="s3v4"),
                )
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                raise
        return self._client

    def _sanitize_filename(self, filename: str) -> str:
        clean_name = os.path.basename(filename).strip().replace(" ", "_")
        return clean_name or "uploaded_file"

    def save_file(
        self,
        file_obj: BinaryIO,
        original_filename: str,
        content_type: str,
        subfolder: str = "documents",
    ) -> Tuple[str, str, int]:
        clean_filename = self._sanitize_filename(original_filename)
        unique_key = f"{subfolder}/{uuid.uuid4().hex}_{clean_filename}"

        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        # Read content and compute SHA-256
        content = file_obj.read()
        total_bytes = len(content)

        if total_bytes > settings.MAX_UPLOAD_SIZE_BYTES:
            raise FileTooLargeException(
                max_bytes=settings.MAX_UPLOAD_SIZE_BYTES,
                actual_bytes=total_bytes,
            )

        sha256_hash = hashlib.sha256(content).hexdigest()

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=unique_key,
                Body=content,
                ContentType=content_type,
            )
            # Also write to local cache for immediate worker processing
            local_cached = self.cache_dir / unique_key
            local_cached.parent.mkdir(parents=True, exist_ok=True)
            with open(local_cached, "wb") as f:
                f.write(content)

            logger.info(
                f"Uploaded file '{original_filename}' to S3 bucket '{self.bucket_name}' key '{unique_key}' ({total_bytes} bytes)"
            )
            return unique_key, sha256_hash, total_bytes
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise

    def get_file_path(self, relative_path: str) -> str:
        local_cached = self.cache_dir / relative_path
        if local_cached.exists():
            return str(local_cached)

        local_cached.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.client.download_file(self.bucket_name, relative_path, str(local_cached))
            return str(local_cached)
        except Exception as e:
            logger.error(f"Failed to download '{relative_path}' from S3: {e}")
            raise InvalidFileException(f"Could not retrieve file '{relative_path}' from cloud storage.")

    def delete_file(self, relative_path: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=relative_path)
            local_cached = self.cache_dir / relative_path
            if local_cached.exists():
                local_cached.unlink()
            return True
        except Exception as e:
            logger.error(f"Failed to delete S3 file '{relative_path}': {e}")
            return False

    def file_exists(self, relative_path: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=relative_path)
            return True
        except Exception:
            return False


def get_storage_service() -> BaseStorageService:
    """Factory to instantiate the configured storage backend."""
    if settings.STORAGE_BACKEND.lower() == "s3" and settings.S3_BUCKET:
        try:
            return S3CompatibleStorageService()
        except Exception as e:
            logger.warning(
                f"Failed to initialize S3CompatibleStorageService ({e}). Falling back to LocalStorageService."
            )
    return LocalStorageService()


storage_service = get_storage_service()
