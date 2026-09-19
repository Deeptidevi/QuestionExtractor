import re
from typing import Optional
from PIL import Image, ImageOps
from app.core.logging import logger


class Normalizer:
    """
    Handles text normalization, OCR artifact correction, whitespace cleanup,
    and image/page orientation normalization.
    """

    # Common OCR mistranscriptions at line beginnings
    OCR_NUMBERING_REPLACEMENTS = [
        (re.compile(r"^([lI\|])\.\s+", re.MULTILINE), r"1. "),
        (re.compile(r"^([lI\|])\)\s+", re.MULTILINE), r"1) "),
        (re.compile(r"^Q\s*([lI\|])\b", re.MULTILINE), r"Q1"),
        (re.compile(r"^Quest[i1]on\s+([lI\|])\b", re.IGNORECASE | re.MULTILINE), r"Question 1"),
    ]

    # Common option letter OCR corrections
    OCR_OPTION_REPLACEMENTS = [
        (re.compile(r"^\(([0O])\)", re.MULTILINE), r"(D)"),
        (re.compile(r"^([0O])\.\s+", re.MULTILINE), r"D. "),
        (re.compile(r"^\[([A-Da-d])\]", re.MULTILINE), r"(\1)"),
    ]

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Cleans whitespace, fixes broken hyphens, and normalizes line breaks."""
        if not text:
            return ""

        # Normalize carriage returns
        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")

        # Fix hyphenated words broken across line breaks (e.g., "examina-\ntion" -> "examination")
        cleaned = re.sub(r"(\b\w+)-\n(\w+\b)", r"\1\2", cleaned)

        # Collapse multiple horizontal whitespace while preserving newlines
        lines = []
        for line in cleaned.split("\n"):
            line_clean = re.sub(r"[ \t]+", " ", line).strip()
            lines.append(line_clean)

        # Collapse excessive consecutive blank lines to at most 2
        result = "\n".join(lines)
        result = re.sub(r"\n{3,}", "\n\n", result)
        return result.strip()

    @classmethod
    def correct_ocr_artifacts(cls, text: str) -> str:
        """Applies safe heuristic corrections to common OCR noise."""
        if not text:
            return ""

        normalized = text
        for pattern, repl in cls.OCR_NUMBERING_REPLACEMENTS:
            normalized = pattern.sub(repl, normalized)

        for pattern, repl in cls.OCR_OPTION_REPLACEMENTS:
            normalized = pattern.sub(repl, normalized)

        return normalized

    @classmethod
    def normalize_image_orientation(cls, image_path: str, output_path: Optional[str] = None) -> str:
        """Rotates image based on EXIF metadata if present, and ensures RGB mode."""
        target_path = output_path or image_path
        try:
            with Image.open(image_path) as img:
                # Transpose EXIF orientation automatically
                transposed = ImageOps.exif_transpose(img)
                if transposed is None:
                    transposed = img

                # Convert to RGB if needed
                if transposed.mode not in ("RGB", "L"):
                    transposed = transposed.convert("RGB")

                transposed.save(target_path)
                return target_path
        except Exception as e:
            logger.warning(f"Could not normalize image orientation for '{image_path}': {e}")
            return image_path
