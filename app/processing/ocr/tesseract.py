import shutil
from PIL import Image
import pytesseract
from app.core.config import settings
from app.core.logging import logger
from app.processing.ocr.base import BaseOCRProvider, OCRResult


class TesseractOCRProvider(BaseOCRProvider):
    """
    Tesseract OCR implementation using pytesseract with bounding boxes and confidence estimation.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.tesseract_cmd = tesseract_cmd or settings.TESSERACT_CMD
        if shutil.which(self.tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def is_available(self) -> bool:
        return bool(shutil.which(self.tesseract_cmd))

    def extract_text_from_image(self, image_path: str, lang: str = "eng") -> OCRResult:
        if not self.is_available():
            logger.warning(
                f"Tesseract executable '{self.tesseract_cmd}' not found in PATH. Returning empty OCR."
            )
            return OCRResult(text="", confidence=0.0, metadata={"warning": "Tesseract not installed"})

        try:
            with Image.open(image_path) as img:
                # Extract detailed data dictionary (words, confidences, boxes)
                data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
                
                # Calculate weighted average confidence of detected words
                confidences = [
                    float(conf)
                    for conf in data.get("conf", [])
                    if str(conf).replace("-1", "").strip() and float(conf) >= 0
                ]
                avg_confidence = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.0

                full_text = pytesseract.image_to_string(img, lang=lang)

                words = []
                n_boxes = len(data["text"])
                for i in range(n_boxes):
                    if int(data["conf"][i]) > 0 and data["text"][i].strip():
                        words.append({
                            "text": data["text"][i],
                            "confidence": float(data["conf"][i]) / 100.0,
                            "bbox": [data["left"][i], data["top"][i], data["left"][i] + data["width"][i], data["top"][i] + data["height"][i]],
                            "line_num": data["line_num"][i],
                        })

                return OCRResult(
                    text=full_text,
                    confidence=max(0.0, min(1.0, avg_confidence)),
                    words=words,
                    metadata={"engine": "tesseract", "lang": lang, "word_count": len(words)},
                )
        except Exception as e:
            logger.error(f"Tesseract OCR failed on image '{image_path}': {e}", exc_info=True)
            return OCRResult(text="", confidence=0.0, metadata={"error": str(e)})
