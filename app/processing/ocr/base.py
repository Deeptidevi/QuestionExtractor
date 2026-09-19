import abc
from typing import Any, Dict, List, Optional


class OCRResult:
    def __init__(
        self,
        text: str,
        confidence: float,
        words: Optional[List[Dict[str, Any]]] = None,
        lines: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.text = text
        self.confidence = confidence
        self.words = words or []
        self.lines = lines or []
        self.metadata = metadata or {}


class BaseOCRProvider(abc.ABC):
    """Abstract interface for pluggable OCR engines."""

    @abc.abstractmethod
    def extract_text_from_image(self, image_path: str, lang: str = "eng") -> OCRResult:
        """Extracts text and word/line-level confidence scores from an image file."""
        pass

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Returns True if the OCR engine is installed and accessible."""
        pass
