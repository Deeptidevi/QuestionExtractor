from typing import Any, Dict, List, Optional
from app.processing.ocr.base import BaseOCRProvider, OCRResult


class MockOCRProvider(BaseOCRProvider):
    """
    Mock OCR provider used for deterministic unit & integration tests.
    """

    def __init__(
        self,
        mock_text: str = "1. What is the capital of France?\nA. London\nB. Paris\nC. Berlin\nD. Rome",
        mock_confidence: float = 0.95,
    ):
        self.mock_text = mock_text
        self.mock_confidence = mock_confidence
        self.call_count = 0

    def is_available(self) -> bool:
        return True

    def extract_text_from_image(self, image_path: str, lang: str = "eng") -> OCRResult:
        self.call_count += 1
        return OCRResult(
            text=self.mock_text,
            confidence=self.mock_confidence,
            words=[
                {"text": word, "confidence": self.mock_confidence, "bbox": [10, 10, 50, 30]}
                for word in self.mock_text.split()
            ],
            metadata={"mock": True, "call_count": self.call_count},
        )
