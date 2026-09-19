import os
import mimetypes
from pathlib import Path
from typing import BinaryIO, Dict, Tuple
from app.core.config import settings
from app.core.exceptions import InvalidFileException, UnsupportedFileTypeException, FileTooLargeException
from app.core.logging import logger

# Magic byte signatures for robust format validation
MAGIC_SIGNATURES = {
    "application/pdf": [b"%PDF"],
    "image/jpeg": [b"\xFF\xD8\xFF"],
    "image/jpg": [b"\xFF\xD8\xFF"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
}

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


class FileValidator:
    """
    Validates uploaded file MIME types, magic byte signatures, safe extensions,
    and size constraints to prevent malicious or malformed uploads.
    """

    @classmethod
    def validate_upload(
        cls,
        file_obj: BinaryIO,
        filename: str,
        content_type: str,
        file_size: int,
    ) -> Tuple[str, str]:
        """
        Validates file metadata and binary magic header.
        Returns normalized (content_type, extension).
        """
        # 1. Size check
        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise FileTooLargeException(
                max_bytes=settings.MAX_UPLOAD_SIZE_BYTES,
                actual_bytes=file_size,
            )
        if file_size <= 0:
            raise InvalidFileException("Uploaded file is empty (0 bytes).")

        # 2. Extension check
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeException(content_type or ext)

        # 3. Read header for magic byte verification
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        
        header = file_obj.read(16)
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)

        # Normalize mime type
        normalized_mime = cls._detect_mime_from_header(header, ext, content_type)
        
        if normalized_mime not in settings.ALLOWED_MIME_TYPES:
            raise UnsupportedFileTypeException(normalized_mime)

        logger.info(f"Validated file '{filename}': {normalized_mime}, {file_size} bytes")
        return normalized_mime, ext

    @classmethod
    def _detect_mime_from_header(cls, header: bytes, ext: str, fallback_mime: str) -> str:
        # Check PDF header
        if header.startswith(b"%PDF"):
            return "application/pdf"
        
        # Check PNG header
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        
        # Check JPEG header
        if header.startswith(b"\xFF\xD8\xFF"):
            return "image/jpeg"

        # If header couldn't match exactly, fallback to extension mapping
        guessed_type, _ = mimetypes.guess_type(f"file{ext}")
        if guessed_type in settings.ALLOWED_MIME_TYPES:
            return guessed_type

        return fallback_mime or "application/octet-stream"
