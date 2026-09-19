import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any, Dict


class StructuredJSONFormatter(logging.Formatter):
    """
    Format logs as structured JSON objects for production observability.
    Strips out sensitive keys (passwords, tokens, secrets).
    """
    SENSITIVE_KEYS = {"password", "secret", "token", "access_token", "api_key", "authorization"}

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Include custom extra fields if attached
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "document_id"):
            log_data["document_id"] = str(record.document_id)
        if hasattr(record, "job_id"):
            log_data["job_id"] = str(record.job_id)
        if hasattr(record, "stage"):
            log_data["stage"] = record.stage
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Sanitize sensitive fields if any were added to record.__dict__
        for key in self.SENSITIVE_KEYS:
            if key in log_data:
                log_data[key] = "[REDACTED]"

        return json.dumps(log_data)


def setup_logging(debug: bool = False) -> logging.Logger:
    level = logging.DEBUG if debug else logging.INFO
    logger = logging.getLogger("doc_processor")
    logger.setLevel(level)

    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(StructuredJSONFormatter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
