from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception with structured error payload."""
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": error_code,
                    "message": message,
                    "details": details or {},
                }
            },
        )
        self.error_code = error_code
        self.message = message
        self.details = details or {}


class AuthenticationException(AppException):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_FAILED",
            message=message,
        )


class PermissionDeniedException(AppException):
    def __init__(self, message: str = "Not authorized to perform this operation"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="PERMISSION_DENIED",
            message=message,
        )


class ResourceNotFoundException(AppException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message=f"{resource} with id '{resource_id}' was not found.",
            details={"resource": resource, "id": resource_id},
        )


class InvalidFileException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_FILE",
            message=message,
            details=details,
        )


class UnsupportedFileTypeException(AppException):
    def __init__(self, mime_type: str):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error_code="UNSUPPORTED_FILE_TYPE",
            message="Only PDF, JPG, JPEG, and PNG files are supported.",
            details={"received_mime_type": mime_type},
        )


class FileTooLargeException(AppException):
    def __init__(self, max_bytes: int, actual_bytes: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            error_code="FILE_TOO_LARGE",
            message=f"File exceeds maximum allowed size of {max_bytes / (1024 * 1024):.1f} MB.",
            details={"max_bytes": max_bytes, "actual_bytes": actual_bytes},
        )


class ConflictException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="RESOURCE_CONFLICT",
            message=message,
            details=details,
        )


class ProcessingException(AppException):
    def __init__(self, message: str, stage: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="PROCESSING_ERROR",
            message=message,
            details={"stage": stage, **(details or {})},
        )
