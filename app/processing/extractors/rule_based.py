import re
from typing import Any, Dict, List, Optional, Tuple
from app.core.logging import logger
from app.db.models.question import QuestionType, ExtractionStatus
from app.processing.extractors.base import BaseQuestionExtractor, RawQuestionCandidate
from app.processing.option_extractor import OptionExtractor


class RuleBasedExtractor(BaseQuestionExtractor):
    """
    Robust rule-based question segmenter supporting diverse numbering patterns,
    multiline questions, cross-page continuity, option extraction, and question type classification.
    """

    # Supported Question Header Patterns
    # Examples: "1.", "Q1.", "Q.1", "Question 1:", "1)", "1:", "1 -", "Item 1."
    QUESTION_START_PATTERNS = [
        # "Question 1:" or "Question 1." or "Question 1"
        re.compile(r"^(?:Question|Problem|Task|Item)\s+([0-9]{1,3})[\.:\s\-]+(?:\((?:\d+|[a-zA-Z]+)\s*marks?\))?\s*(.*)$", re.IGNORECASE),
        # "Q1." or "Q1:" or "Q.1" or "Q-1"
        re.compile(r"^Q[\.\-_]?\s*([0-9]{1,3})[\.:\s\-]+(?:\((?:\d+|[a-zA-Z]+)\s*marks?\))?\s*(.*)$", re.IGNORECASE),
        # "1." or "1)" or "1:" or "1 -"
        re.compile(r"^([0-9]{1,3})[\.\)\:\-]\s+(.*)$"),
        # "[1]" or "(1)" at the start of line
        re.compile(r"^(?:\[|\()([0-9]{1,3})(?:\]|\))\s+(.*)$"),
    ]

    # Patterns indicating exam headers, instructions, or answer key blocks (should NOT be treated as questions)
    HEADER_IGNORE_PATTERNS = [
        re.compile(r"^(?:Section|Part|Group|Module|Unit)\b.*", re.IGNORECASE),
        re.compile(r"^(?:Instructions?|Directions?|Maximum Marks?|Time Allowed|Total Marks?|Duration|Date|Subject|Course|Department|University|College|School|Class)\b", re.IGNORECASE),
        re.compile(r".*(?:EXAMINATION|ASSESSMENT|MID-TERM|FINAL EXAM|QUESTION PAPER|TEST PAPER|ALGORITHMS|SCIENCE|PHYSICS|CHEMISTRY|MATHEMATICS).*", re.IGNORECASE),
        re.compile(r"^(?:Answer Key|Answers?|Solutions?|Key to Answers?|Marking Scheme)\b", re.IGNORECASE),
    ]

    def extract_questions(
        self,
        pages_text: List[Dict[str, Any]],
    ) -> List[RawQuestionCandidate]:
        """
        Segments questions sequentially across all document pages.
        Handles questions that start on page N and continue on page N+1.
        """
        raw_candidates: List[RawQuestionCandidate] = []
        
        current_number: Optional[str] = None
        current_lines: List[str] = []
        current_pages: List[int] = []
        seq_counter = 1

        for page_info in pages_text:
            page_num = page_info["page_number"]
            page_text = page_info.get("text", "") or ""
            
            lines = page_text.split("\n")
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    if current_lines:
                        current_lines.append("")
                    continue

                # Check if this line is an answer key or ignored header
                if any(p.match(stripped) for p in self.HEADER_IGNORE_PATTERNS):
                    # If this is an Answer Key header, flush active question
                    if re.match(r"^(?:Answer Key|Answers?|Solutions?|Key to Answers?|Marking Scheme)\b", stripped, re.IGNORECASE):
                        if current_lines:
                            cand = self._build_candidate(
                                current_number,
                                seq_counter,
                                current_lines,
                                current_pages,
                            )
                            if cand:
                                raw_candidates.append(cand)
                                seq_counter += 1
                            current_number = None
                            current_lines = []
                            current_pages = []
                    continue

                # Test if line matches a new question start
                matched_num = None
                matched_content = None

                for pattern in self.QUESTION_START_PATTERNS:
                    match = pattern.match(stripped)
                    if match:
                        matched_num = match.group(1)
                        matched_content = match.group(2).strip()
                        break

                if matched_num:
                    # Flush previous question
                    if current_lines:
                        cand = self._build_candidate(
                            current_number,
                            seq_counter,
                            current_lines,
                            current_pages,
                        )
                        if cand:
                            raw_candidates.append(cand)
                            seq_counter += 1

                    # Start new question
                    current_number = matched_num
                    current_lines = [matched_content] if matched_content else [stripped]
                    current_pages = [page_num]
                else:
                    if current_lines:
                        # Append to active question
                        current_lines.append(stripped)
                        if page_num not in current_pages:
                            current_pages.append(page_num)
                    else:
                        # Unnumbered question body (only if question-like, e.g. contains '?' or option choices)
                        is_question_like = "?" in stripped or "What " in stripped or "Which " in stripped or "Explain " in stripped
                        if len(stripped) > 20 and is_question_like and not any(p.match(stripped) for p in self.HEADER_IGNORE_PATTERNS):
                            current_number = None
                            current_lines = [stripped]
                            current_pages = [page_num]

        # Flush trailing question
        if current_lines:
            cand = self._build_candidate(
                current_number,
                seq_counter,
                current_lines,
                current_pages,
            )
            if cand:
                raw_candidates.append(cand)

        logger.info(f"RuleBasedExtractor segmented {len(raw_candidates)} questions.")
        return raw_candidates

    def _build_candidate(
        self,
        q_num: Optional[str],
        seq_order: int,
        lines: List[str],
        pages: List[int],
    ) -> Optional[RawQuestionCandidate]:
        raw_text = "\n".join(lines).strip()
        if not raw_text or len(raw_text) < 5:
            return None

        # Extract options and question stem
        stem, options = OptionExtractor.extract_options_from_block(raw_text)
        if not stem and options:
            stem = raw_text

        # Detect question type
        q_type = self._classify_question_type(stem, options)

        # Build confidence and warnings
        warnings = []
        confidence = 0.95

        if not q_num:
            warnings.append("MISSING_QUESTION_NUMBER")
            confidence -= 0.20

        if len(pages) > 1:
            warnings.append("QUESTION_CONTINUES_NEXT_PAGE")

        if q_type == QuestionType.MCQ and len(options) < 2:
            warnings.append("OPTIONS_UNCERTAIN")
            confidence -= 0.20

        review_required = confidence < 0.60 or "MISSING_QUESTION_NUMBER" in warnings

        status = ExtractionStatus.SUCCESS
        if review_required:
            status = ExtractionStatus.REVIEW_REQUIRED
        elif len(warnings) > 0:
            status = ExtractionStatus.PARTIAL

        return RawQuestionCandidate(
            question_number=q_num,
            sequence_order=seq_order,
            raw_text=raw_text,
            question_text=stem,
            question_type=q_type,
            options=options,
            source_pages=sorted(list(set(pages))),
            confidence=max(0.1, min(1.0, confidence)),
            extraction_status=status,
            review_required=review_required,
            warnings=warnings,
        )

    def _classify_question_type(
        self,
        stem: str,
        options: List[Dict[str, Any]],
    ) -> QuestionType:
        stem_lower = stem.lower()

        # True / False
        if "true or false" in stem_lower or "state true/false" in stem_lower:
            return QuestionType.TRUE_FALSE
        if len(options) == 2:
            opt_texts = {opt["text"].strip().lower() for opt in options}
            if opt_texts == {"true", "false"} or opt_texts == {"yes", "no"}:
                return QuestionType.TRUE_FALSE

        # Multiple Choice
        if len(options) >= 2:
            return QuestionType.MCQ

        # Fill in the blank
        if "____" in stem or "[blank]" in stem_lower or "fill in the blank" in stem_lower:
            return QuestionType.FILL_IN_THE_BLANK

        # Matching
        if "match column" in stem_lower or "match the following" in stem_lower:
            return QuestionType.MATCHING

        # Long Answer vs Short Answer
        if any(keyword in stem_lower for keyword in ["explain in detail", "discuss", "elaborate", "write an essay"]):
            return QuestionType.LONG_ANSWER
        
        if any(keyword in stem_lower for keyword in ["what is", "define", "name the", "give two examples", "calculate", "consider a"]):
            return QuestionType.SHORT_ANSWER

        return QuestionType.SHORT_ANSWER if len(stem) > 20 else QuestionType.UNKNOWN
