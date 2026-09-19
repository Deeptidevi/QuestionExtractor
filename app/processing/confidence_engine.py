from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import logger
from app.db.models.question import QuestionType, ExtractionStatus


class ConfidenceScore:
    def __init__(
        self,
        overall_score: float,
        signals: Dict[str, float],
        status: ExtractionStatus,
        review_required: bool,
    ):
        self.overall_score = overall_score
        self.signals = signals
        self.status = status
        self.review_required = review_required


class ConfidenceEngine:
    """
    Computes a weighted, multi-signal confidence score for extracted questions and documents.
    Signals:
    1. Numbering Clarity (25%): Valid detected question number and sequence.
    2. Option Integrity (25%): Valid distinct options (A-D, etc.) for MCQs.
    3. Text Quality & OCR (20%): Low OCR error rate, proper punctuation, reasonable length.
    4. Boundary Certainty (15%): Unbroken lines, no abrupt cutoffs.
    5. Continuity & Layout (15%): Normal page transitions, layout structure.
    """

    # Signal Weights
    WEIGHT_NUMBERING = 0.25
    WEIGHT_OPTIONS = 0.25
    WEIGHT_TEXT_QUALITY = 0.20
    WEIGHT_BOUNDARIES = 0.15
    WEIGHT_CONTINUITY = 0.15

    @classmethod
    def calculate_question_confidence(
        cls,
        question_number: Optional[str],
        question_text: str,
        question_type: QuestionType,
        options: List[Dict[str, Any]],
        source_pages: List[int],
        ocr_confidence: float = 1.0,
    ) -> ConfidenceScore:
        signals: Dict[str, float] = {}

        # 1. Numbering Signal
        if question_number and question_number.isdigit():
            signals["numbering"] = 1.0
        elif question_number:
            signals["numbering"] = 0.85
        else:
            signals["numbering"] = 0.20  # Missing number is a strong uncertainty signal

        # 2. Option Signal
        if question_type == QuestionType.MCQ:
            if len(options) >= 4:
                signals["options"] = 1.0
            elif len(options) == 3:
                signals["options"] = 0.75
            elif len(options) == 2:
                signals["options"] = 0.50
            else:
                signals["options"] = 0.10
        elif question_type == QuestionType.TRUE_FALSE:
            signals["options"] = 1.0 if len(options) == 2 else 0.80
        else:
            signals["options"] = 1.0  # Non-choice questions don't require options

        # 3. Text Quality Signal (incorporating OCR engine score)
        text_len = len(question_text.strip())
        if text_len > 30 and ocr_confidence > 0.80:
            signals["text_quality"] = min(1.0, ocr_confidence)
        elif text_len > 10:
            signals["text_quality"] = min(0.70, max(0.30, ocr_confidence))
        else:
            signals["text_quality"] = 0.20

        # 4. Boundary Certainty Signal
        # Check if question ends with reasonable punctuation or option block
        has_punctuation = question_text.rstrip().endswith(("?", ".", ":", "!"))
        signals["boundaries"] = 1.0 if has_punctuation else 0.70

        # 5. Continuity Signal
        if len(source_pages) == 1:
            signals["continuity"] = 1.0
        elif len(source_pages) == 2:
            signals["continuity"] = 0.80  # Spanning 2 pages is common
        else:
            signals["continuity"] = 0.60  # Spanning 3+ pages is unusual

        # Weighted combination
        overall = (
            signals["numbering"] * cls.WEIGHT_NUMBERING
            + signals["options"] * cls.WEIGHT_OPTIONS
            + signals["text_quality"] * cls.WEIGHT_TEXT_QUALITY
            + signals["boundaries"] * cls.WEIGHT_BOUNDARIES
            + signals["continuity"] * cls.WEIGHT_CONTINUITY
        )

        overall = round(max(0.0, min(1.0, overall)), 3)

        # Classification based on configured thresholds
        if overall >= settings.CONFIDENCE_HIGH_THRESHOLD:
            status = ExtractionStatus.SUCCESS
            review_required = False
        elif overall >= settings.CONFIDENCE_MEDIUM_THRESHOLD:
            status = ExtractionStatus.PARTIAL
            review_required = overall < settings.CONFIDENCE_REVIEW_THRESHOLD
        else:
            status = ExtractionStatus.REVIEW_REQUIRED
            review_required = True

        # Extra safety guard: missing question numbers or critical option gaps always flag review
        if not question_number or (question_type == QuestionType.MCQ and len(options) < 2):
            review_required = True
            status = ExtractionStatus.REVIEW_REQUIRED

        return ConfidenceScore(
            overall_score=overall,
            signals=signals,
            status=status,
            review_required=review_required,
        )

    @classmethod
    def calculate_document_overall_confidence(
        cls,
        question_scores: List[ConfidenceScore],
        page_ocr_confidences: List[float],
    ) -> float:
        if not question_scores and not page_ocr_confidences:
            return 0.0

        q_avg = (
            sum(q.overall_score for q in question_scores) / len(question_scores)
            if question_scores
            else 0.5
        )
        page_avg = (
            sum(page_ocr_confidences) / len(page_ocr_confidences)
            if page_ocr_confidences
            else 1.0
        )

        overall = round(0.7 * q_avg + 0.3 * page_avg, 3)
        return max(0.0, min(1.0, overall))
