from typing import Optional
from app.core.config import settings
from app.processing.ocr.base import BaseOCRProvider, OCRResult
from app.processing.ocr.tesseract import TesseractOCRProvider
from app.processing.ocr.mock_ocr import MockOCRProvider


def get_ocr_provider(provider_type: Optional[str] = None) -> BaseOCRProvider:
    name = (provider_type or settings.OCR_PROVIDER).lower()
    if name == "mock":
        return MockOCRProvider()
    elif name == "tesseract":
        return TesseractOCRProvider()
    else:
        return TesseractOCRProvider()


__all__ = [
    "BaseOCRProvider",
    "OCRResult",
    "TesseractOCRProvider",
    "MockOCRProvider",
    "get_ocr_provider",
]
