import re
from typing import Any, Dict, List, Optional
from app.core.logging import logger


class DetectedAnswerItem:
    def __init__(
        self,
        question_number: str,
        answer_value: str,
        raw_text: str,
        source_page: int,
        confidence: float = 0.95,
        explanation: Optional[str] = None,
    ):
        self.question_number = question_number
        self.answer_value = answer_value
        self.raw_text = raw_text
        self.source_page = source_page
        self.confidence = confidence
        self.explanation = explanation


class AnswerKeyDetector:
    """
    Detects and extracts answer key entries from document sections,
    dedicated answer key pages, or standalone answer key documents.
    """

    # Headers signaling answer keys
    ANSWER_KEY_HEADERS = [
        re.compile(r"^(?:Answer\s*Key|Answers?|Solutions?|Key\s*to\s*Answers?|Marking\s*Scheme)\b", re.IGNORECASE),
    ]

    # Individual answer mapping formats:
    # 1. "1-A", "1 - A", "1-C", "1: B", "1. C", "1 - E"
    # 2. "Q1 A", "Q1: C", "Q.1 - B"
    # 3. "1. (A)", "1.(b)"
    # 4. "1. True", "2. False"
    ANSWER_ENTRY_PATTERNS = [
        # "1 - A" or "1-A" or "1: A" or "1. A" or "1. (A)" or "1. [A]"
        re.compile(r"^(?:Q[\.\-_]?)?\s*([0-9]{1,3})[\.\:\-\s]+\(?([A-Za-z0-9]|True|False|TRUE|FALSE)\)?(?:\s*[\:\-]\s*(.*))?$"),
        # "Q1: C" or "Q1 C"
        re.compile(r"^Q\s*([0-9]{1,3})\s*[\:\-\s]+\(?([A-Za-z0-9]|True|False)\)?(?:\s*[\:\-]\s*(.*))?$", re.IGNORECASE),
        # Grid format: "1. A   2. B   3. C   4. D"
        re.compile(r"(?:^|\s+)(?:Q[\.\-_]?)?([0-9]{1,3})[\.\:\-\)]\s*\(?([A-Za-z]|True|False)\)?"),
    ]

    @classmethod
    def detect_answers_in_document(
        cls,
        pages_text: List[Dict[str, Any]],
    ) -> List[DetectedAnswerItem]:
        """
        Scans all document pages for Answer Key sections or tabular grids.
        """
        detected_answers: List[DetectedAnswerItem] = []

        for page_info in pages_text:
            page_num = page_info["page_number"]
            text = page_info.get("text", "") or ""
            
            lines = text.split("\n")
            in_answer_key_section = False

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                # Check if header matches Answer Key
                if any(h.match(stripped) for h in cls.ANSWER_KEY_HEADERS):
                    in_answer_key_section = True
                    logger.info(f"Found Answer Key section on page {page_num}: '{stripped}'")
                    continue

                # Check for grid-style multiple answers on a single line: "1. A  2. B  3. C"
                grid_matches = list(cls.ANSWER_ENTRY_PATTERNS[2].finditer(stripped))
                if len(grid_matches) >= 2 or (in_answer_key_section and len(grid_matches) >= 1):
                    for m in grid_matches:
                        q_num = m.group(1).strip()
                        val = m.group(2).strip().upper()
                        detected_answers.append(
                            DetectedAnswerItem(
                                question_number=q_num,
                                answer_value=val,
                                raw_text=m.group(0).strip(),
                                source_page=page_num,
                                confidence=0.95 if in_answer_key_section else 0.85,
                            )
                        )
                    continue

                # Check single entry patterns
                if in_answer_key_section:
                    matched = False
                    for pattern in cls.ANSWER_ENTRY_PATTERNS[:2]:
                        m = pattern.match(stripped)
                        if m:
                            q_num = m.group(1).strip()
                            val = m.group(2).strip().upper()
                            explanation = m.group(3).strip() if len(m.groups()) >= 3 and m.group(3) else None
                            detected_answers.append(
                                DetectedAnswerItem(
                                    question_number=q_num,
                                    answer_value=val,
                                    raw_text=stripped,
                                    source_page=page_num,
                                    confidence=0.95,
                                    explanation=explanation,
                                )
                            )
                            matched = True
                            break

        logger.info(f"AnswerKeyDetector found {len(detected_answers)} answers.")
        return detected_answers
