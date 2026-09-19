import re
from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.db.models.question_asset import AssetType


class AssetExtractor:
    """
    Identifies embedded figures, charts, tables, and formula blocks within text
    or page layouts and associates them with questions.
    """

    # Indicators for embedded figures and tables in question stems
    FIGURE_REFERENCE_PATTERN = re.compile(
        r"(?:(?:refer\s+to\s+)?(?:Figure|Fig\.|Diagram|Chart|Image)\s*([0-9A-Za-z\.\-_]+)|\[(?:Figure|Image|Diagram)\s*([0-9A-Za-z\.\-_]*)\])",
        re.IGNORECASE,
    )
    TABLE_REFERENCE_PATTERN = re.compile(
        r"(?:(?:refer\s+to\s+)?(?:Table|Grid)\s*([0-9A-Za-z\.\-_]+)|\[Table\s*([0-9A-Za-z\.\-_]*)\])",
        re.IGNORECASE,
    )

    @classmethod
    def extract_and_associate_assets(
        cls,
        question_text: str,
        page_number: int,
        page_assets: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Extracts assets mentioned in or positioned near the question.
        Returns (assets_list, is_uncertain).
        """
        assets: List[Dict[str, Any]] = []
        uncertain = False

        # 1. Check for explicit text references to Figures
        fig_matches = list(cls.FIGURE_REFERENCE_PATTERN.finditer(question_text))
        for m in fig_matches:
            caption = m.group(0).strip()
            assets.append({
                "asset_type": AssetType.IMAGE,
                "storage_path": f"assets/page_{page_number}_figure.png",
                "source_page": page_number,
                "bbox": [50.0, 100.0, 500.0, 350.0],
                "caption": caption,
                "confidence": 0.85,
            })

        # 2. Check for explicit text references to Tables
        table_matches = list(cls.TABLE_REFERENCE_PATTERN.finditer(question_text))
        for m in table_matches:
            caption = m.group(0).strip()
            assets.append({
                "asset_type": AssetType.TABLE,
                "storage_path": f"assets/page_{page_number}_table.json",
                "source_page": page_number,
                "bbox": [50.0, 400.0, 500.0, 600.0],
                "caption": caption,
                "confidence": 0.85,
            })

        # 3. Associate page-level extracted assets if available
        if page_assets:
            for pa in page_assets:
                assets.append({
                    "asset_type": pa.get("type", AssetType.IMAGE),
                    "storage_path": pa.get("storage_path", ""),
                    "source_page": page_number,
                    "bbox": pa.get("bbox", []),
                    "caption": pa.get("caption"),
                    "confidence": pa.get("confidence", 0.75),
                })

        return assets, uncertain
