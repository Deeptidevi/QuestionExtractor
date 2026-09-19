import re
from typing import Any, Dict, List, Tuple
from app.core.logging import logger


class OptionExtractor:
    """
    Detects and extracts multiple-choice options across various styles:
    - 'A. ...', 'B. ...', 'C. ...', 'D. ...'
    - '(A) ...', '(B) ...', '(C) ...', '(D) ...'
    - '(a) ...', '(b) ...', '(c) ...', '(d) ...'
    - 'a) ...', 'b) ...', 'c) ...', 'd) ...'
    - '[A] ...', '[B] ...'
    - '1. ...', '2. ...', '3. ...', '4. ...' (when inside an MCQ question block)
    - Inline options on single line: 'A. Foo  B. Bar  C. Baz  D. Qux'
    """

    # Multi-line start patterns
    OPTION_PATTERNS = [
        # (A) or (a) or (1)
        re.compile(r"^\(([A-Da-d0-9])\)\s*(.+)$"),
        # [A] or [a]
        re.compile(r"^\[([A-Da-d0-9])\]\s*(.+)$"),
        # A. or A) or a)
        re.compile(r"^([A-Da-d])[\.\)]\s+(.+)$"),
        # 1) or 2)
        re.compile(r"^([1-4])\)\s+(.+)$"),
    ]

    # Inline horizontal options e.g. "A. Cat   B. Dog   C. Fish   D. Bird"
    INLINE_OPTION_PATTERN = re.compile(
        r"(?:^|\s+)(?:(?:\(([A-Da-d0-9])\))|([A-Da-d0-9])[\.\)])\s+([^\n\r\t]+?)(?=(?:\s+(?:(?:\([A-Da-d0-9]\))|[A-Da-d0-9][\.\)]\s+))|$)"
    )

    @classmethod
    def extract_options_from_block(
        cls,
        text: str,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Separates the question text stem from its choices/options.
        Returns (question_stem, options_list).
        """
        lines = text.strip().split("\n")
        stem_lines: List[str] = []
        options: List[Dict[str, Any]] = []
        
        in_options = False
        current_label: str = ""
        current_text_parts: List[str] = []
        position = 1

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_options and current_text_parts:
                    current_text_parts.append("")
                continue

            # Check if line contains multiple inline options (e.g. A. ... B. ... C. ...)
            inline_matches = list(cls.INLINE_OPTION_PATTERN.finditer(stripped))
            if len(inline_matches) >= 2:
                # Flush existing accumulated option
                if current_label and current_text_parts:
                    options.append({
                        "label": current_label,
                        "text": " ".join(current_text_parts).strip(),
                        "position": position,
                        "confidence": 0.95,
                    })
                    position += 1
                    current_label = ""
                    current_text_parts = []

                in_options = True
                for m in inline_matches:
                    lbl = (m.group(1) or m.group(2)).upper()
                    val = m.group(3).strip()
                    options.append({
                        "label": lbl,
                        "text": val,
                        "position": position,
                        "confidence": 0.95,
                    })
                    position += 1
                continue

            # Check if line matches a single option start
            matched_label = None
            matched_content = None

            for pattern in cls.OPTION_PATTERNS:
                match = pattern.match(stripped)
                if match:
                    matched_label = match.group(1).upper()
                    matched_content = match.group(2).strip()
                    break

            if matched_label:
                # Flush previous option
                if current_label and current_text_parts:
                    options.append({
                        "label": current_label,
                        "text": " ".join(current_text_parts).strip(),
                        "position": position,
                        "confidence": 0.95,
                    })
                    position += 1

                in_options = True
                current_label = matched_label
                current_text_parts = [matched_content]
            else:
                if in_options:
                    # Multi-line continuation of current option
                    current_text_parts.append(stripped)
                else:
                    stem_lines.append(stripped)

        # Flush final option
        if current_label and current_text_parts:
            options.append({
                "label": current_label,
                "text": " ".join(current_text_parts).strip(),
                "position": position,
                "confidence": 0.95,
            })

        question_stem = "\n".join(stem_lines).strip()
        return question_stem, options
