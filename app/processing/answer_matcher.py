from typing import Any, Dict, List, Optional, Tuple
from app.core.logging import logger
from app.db.models.answer import AnswerMatchStatus
from app.processing.extractors.base import RawQuestionCandidate
from app.processing.answer_key_detector import DetectedAnswerItem


class MatchResult:
    def __init__(
        self,
        question: RawQuestionCandidate,
        answer: Optional[DetectedAnswerItem] = None,
        match_status: AnswerMatchStatus = AnswerMatchStatus.UNMATCHED,
        confidence: float = 0.0,
        warning: Optional[str] = None,
    ):
        self.question = question
        self.answer = answer
        self.match_status = match_status
        self.confidence = confidence
        self.warning = warning


class AnswerMatcher:
    """
    Correlates extracted questions with detected answer keys based on question numbers,
    sequence positions, option validation, and fuzzy matching.
    """

    @classmethod
    def match_answers(
        cls,
        questions: List[RawQuestionCandidate],
        answers: List[DetectedAnswerItem],
    ) -> List[MatchResult]:
        results: List[MatchResult] = []
        
        # Build lookup map by question_number string
        answers_by_num: Dict[str, List[DetectedAnswerItem]] = {}
        for ans in answers:
            q_num = ans.question_number.strip()
            answers_by_num.setdefault(q_num, []).append(ans)

        used_answer_indices = set()

        for q in questions:
            q_num = (q.question_number or "").strip()
            matched_item: Optional[DetectedAnswerItem] = None
            status = AnswerMatchStatus.UNMATCHED
            conf = 0.0
            warning = None

            if q_num and q_num in answers_by_num:
                candidates = answers_by_num[q_num]
                if len(candidates) == 1:
                    matched_item = candidates[0]
                    # Validate answer validity if it's an MCQ option
                    valid_labels = {opt["label"].upper() for opt in q.options}
                    if valid_labels and matched_item.answer_value.upper() not in valid_labels:
                        # Option letter does not match available options (e.g. key has 'E' but question has only A-D)
                        status = AnswerMatchStatus.AMBIGUOUS
                        conf = 0.40
                        warning = "ANSWER_MATCH_UNCERTAIN"
                        logger.warning(
                            f"Answer '{matched_item.answer_value}' for Q{q_num} does not match valid options {valid_labels}"
                        )
                    else:
                        status = AnswerMatchStatus.EXACT_MATCH
                        conf = matched_item.confidence
                else:
                    # Multiple conflicting answers found for same question number
                    status = AnswerMatchStatus.AMBIGUOUS
                    conf = 0.30
                    warning = "ANSWER_MATCH_UNCERTAIN"
                    matched_item = None
            else:
                # No answer key found for this question
                warning = "ANSWER_NOT_FOUND"

            # If matching is ambiguous or uncertain, do NOT assign answer directly
            if status == AnswerMatchStatus.AMBIGUOUS:
                matched_item = None

            results.append(
                MatchResult(
                    question=q,
                    answer=matched_item,
                    match_status=status,
                    confidence=conf,
                    warning=warning,
                )
            )

        return results
