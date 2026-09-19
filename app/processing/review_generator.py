from typing import Any, Dict, List, Optional
from app.db.models.review_item import WarningType, ReviewSeverity
from app.processing.extractors.base import RawQuestionCandidate
from app.processing.confidence_engine import ConfidenceScore
from app.processing.answer_matcher import MatchResult


class GeneratedReviewWarning:
    def __init__(
        self,
        warning_type: WarningType,
        severity: ReviewSeverity,
        message: str,
        question_index: Optional[int] = None,
        source_page: Optional[int] = None,
        confidence: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.warning_type = warning_type
        self.severity = severity
        self.message = message
        self.question_index = question_index
        self.source_page = source_page
        self.confidence = confidence
        self.details = details or {}


class ReviewItemGenerator:
    """
    Analyzes questions, confidence signals, answer associations, and page layouts
    to produce structured, actionable review items for human reviewers.
    """

    @classmethod
    def generate_review_items(
        cls,
        match_results: List[MatchResult],
        confidence_scores: List[ConfidenceScore],
        page_stats: List[Dict[str, Any]],
    ) -> List[GeneratedReviewWarning]:
        review_items: List[GeneratedReviewWarning] = []

        # 1. Page-level review signals (e.g. Low OCR confidence)
        for p in page_stats:
            p_num = p.get("page_number", 1)
            ocr_conf = p.get("ocr_confidence")
            if ocr_conf is not None and ocr_conf < 0.60:
                review_items.append(
                    GeneratedReviewWarning(
                        warning_type=WarningType.LOW_OCR_CONFIDENCE,
                        severity=ReviewSeverity.WARNING,
                        message=f"Page {p_num} had low OCR confidence ({ocr_conf:.2f}). Please review extracted text.",
                        source_page=p_num,
                        confidence=ocr_conf,
                        details={"page_number": p_num, "ocr_confidence": ocr_conf},
                    )
                )

        # 2. Question-level review signals
        for idx, match_res in enumerate(match_results):
            q = match_res.question
            conf_score = confidence_scores[idx] if idx < len(confidence_scores) else None
            primary_page = q.source_pages[0] if q.source_pages else 1

            # Missing question number
            if not q.question_number:
                review_items.append(
                    GeneratedReviewWarning(
                        warning_type=WarningType.MISSING_QUESTION_NUMBER,
                        severity=ReviewSeverity.WARNING,
                        message=f"Question at index {q.sequence_order} is missing a clear question number.",
                        question_index=idx,
                        source_page=primary_page,
                        confidence=conf_score.overall_score if conf_score else 0.5,
                        details={"raw_prefix": q.raw_text[:60]},
                    )
                )

            # Cross-page continuation
            if len(q.source_pages) > 1:
                review_items.append(
                    GeneratedReviewWarning(
                        warning_type=WarningType.QUESTION_CONTINUES_NEXT_PAGE,
                        severity=ReviewSeverity.INFO,
                        message=f"Question {q.question_number or idx+1} spans across pages {q.source_pages}.",
                        question_index=idx,
                        source_page=primary_page,
                        confidence=conf_score.overall_score if conf_score else 0.85,
                        details={"pages": q.source_pages},
                    )
                )

            # Option anomalies in MCQs
            if q.question_type.value == "MCQ" and len(q.options) < 4:
                review_items.append(
                    GeneratedReviewWarning(
                        warning_type=WarningType.OPTIONS_UNCERTAIN,
                        severity=ReviewSeverity.WARNING,
                        message=f"Question {q.question_number or idx+1} has only {len(q.options)} choices extracted.",
                        question_index=idx,
                        source_page=primary_page,
                        confidence=conf_score.overall_score if conf_score else 0.6,
                        details={"detected_options": [opt["label"] for opt in q.options]},
                    )
                )

            # Answer matching warnings
            if match_res.warning == "ANSWER_MATCH_UNCERTAIN":
                review_items.append(
                    GeneratedReviewWarning(
                        warning_type=WarningType.ANSWER_MATCH_UNCERTAIN,
                        severity=ReviewSeverity.CRITICAL,
                        message=f"Answer key match for question {q.question_number or idx+1} is ambiguous.",
                        question_index=idx,
                        source_page=primary_page,
                        confidence=match_res.confidence,
                        details={"match_status": match_res.match_status.value},
                    )
                )
            elif match_res.warning == "ANSWER_NOT_FOUND":
                review_items.append(
                    GeneratedReviewWarning(
                        warning_type=WarningType.ANSWER_NOT_FOUND,
                        severity=ReviewSeverity.INFO,
                        message=f"No answer key detected for question {q.question_number or idx+1}.",
                        question_index=idx,
                        source_page=primary_page,
                        confidence=0.0,
                    )
                )

            # Low overall confidence
            if conf_score and conf_score.overall_score < 0.60:
                review_items.append(
                    GeneratedReviewWarning(
                        warning_type=WarningType.PARTIAL_EXTRACTION,
                        severity=ReviewSeverity.WARNING,
                        message=f"Low confidence ({conf_score.overall_score:.2f}) for question {q.question_number or idx+1}.",
                        question_index=idx,
                        source_page=primary_page,
                        confidence=conf_score.overall_score,
                        details=conf_score.signals,
                    )
                )

        return review_items
