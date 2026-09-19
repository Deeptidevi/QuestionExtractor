import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pypdf import PdfReader
from PIL import Image
from app.core.logging import logger
from app.core.exceptions import ProcessingException


class ExtractedPageData:
    def __init__(
        self,
        page_number: int,
        raw_text: str,
        width: float,
        height: float,
        rotation: int = 0,
        image_path: Optional[str] = None,
        is_scanned: bool = False,
    ):
        self.page_number = page_number
        self.raw_text = raw_text
        self.width = width
        self.height = height
        self.rotation = rotation
        self.image_path = image_path
        self.is_scanned = is_scanned


class PageExtractor:
    """
    Extracts individual pages from PDF documents or treats standalone image files
    as 1-page documents with geometric properties.
    """

    @classmethod
    def extract_pages_from_file(
        cls,
        file_path: str,
        mime_type: str,
    ) -> List[ExtractedPageData]:
        if not os.path.exists(file_path):
            raise ProcessingException(f"File not found: {file_path}", stage="PAGE_EXTRACTION")

        if mime_type == "application/pdf":
            return cls._extract_pdf_pages(file_path)
        elif mime_type.startswith("image/"):
            return cls._extract_image_as_page(file_path)
        else:
            raise ProcessingException(f"Unsupported mime type for page extraction: {mime_type}", stage="PAGE_EXTRACTION")

    @classmethod
    def _extract_pdf_pages(cls, file_path: str) -> List[ExtractedPageData]:
        pages = []
        try:
            reader = PdfReader(file_path)
            total = len(reader.pages)
            logger.info(f"Extracting {total} pages from PDF: {file_path}")

            for idx, page in enumerate(reader.pages):
                page_num = idx + 1
                try:
                    text = page.extract_text() or ""
                except Exception as e:
                    logger.warning(f"Error extracting native text on page {page_num}: {e}")
                    text = ""

                # Page dimensions & rotation
                box = page.mediabox
                width = float(box.width) if box else 595.0
                height = float(box.height) if box else 842.0
                rotation = int(page.get("/Rotate", 0) or 0)

                # Determine if page is likely scanned (very low character count)
                is_scanned = len(text.strip()) < 30

                pages.append(
                    ExtractedPageData(
                        page_number=page_num,
                        raw_text=text,
                        width=width,
                        height=height,
                        rotation=rotation,
                        is_scanned=is_scanned,
                    )
                )
            return pages
        except Exception as e:
            logger.error(f"Failed to extract pages from PDF '{file_path}': {e}", exc_info=True)
            raise ProcessingException(f"Corrupted or unreadable PDF: {str(e)}", stage="PAGE_EXTRACTION")

    @classmethod
    def _extract_image_as_page(cls, file_path: str) -> List[ExtractedPageData]:
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                return [
                    ExtractedPageData(
                        page_number=1,
                        raw_text="",
                        width=float(width),
                        height=float(height),
                        rotation=0,
                        image_path=file_path,
                        is_scanned=True,
                    )
                ]
        except Exception as e:
            logger.error(f"Failed to inspect image '{file_path}': {e}", exc_info=True)
            raise ProcessingException(f"Invalid or corrupted image file: {str(e)}", stage="PAGE_EXTRACTION")
