import abc
from typing import Any, Dict, List, Optional
from app.db.models.question import QuestionType, ExtractionStatus


class RawQuestionCandidate:
    def __init__(
        self,
        question_number: Optional[str],
        sequence_order: int,
        raw_text: str,
        question_text: str,
        question_type: QuestionType,
        options: List[Dict[str, Any]],
        source_pages: List[int],
        source_regions: Optional[List[Dict[str, Any]]] = None,
        confidence: float = 1.0,
        extraction_status: ExtractionStatus = ExtractionStatus.SUCCESS,
        review_required: bool = False,
        warnings: Optional[List[str]] = None,
    ):
        self.question_number = question_number
        self.sequence_order = sequence_order
        self.raw_text = raw_text
        self.question_text = question_text
        self.question_type = question_type
        self.options = options
        self.source_pages = source_pages
        self.source_regions = source_regions or []
        self.confidence = confidence
        self.extraction_status = extraction_status
        self.review_required = review_required
        self.warnings = warnings or []


class BaseQuestionExtractor(abc.ABC):
    """Abstract interface for rule-based, AI-based, or hybrid question extractors."""

    @abc.abstractmethod
    def extract_questions(
        self,
        pages_text: List[Dict[str, Any]],  # [{"page_number": 1, "text": "..."}]
    ) -> List[RawQuestionCandidate]:
        """Processes sequential page texts and segments questions."""
        pass
