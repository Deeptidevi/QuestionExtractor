from typing import Optional
from app.core.config import settings
from app.processing.extractors.base import BaseQuestionExtractor, RawQuestionCandidate
from app.processing.extractors.rule_based import RuleBasedExtractor
from app.processing.extractors.ai_extractor import AIQuestionExtractor


def get_question_extractor(engine_name: Optional[str] = None) -> BaseQuestionExtractor:
    name = (engine_name or settings.EXTRACTION_ENGINE).lower()
    if name == "ai":
        return AIQuestionExtractor()
    elif name == "hybrid":
        return AIQuestionExtractor(fallback_extractor=RuleBasedExtractor())
    else:
        return RuleBasedExtractor()


__all__ = [
    "BaseQuestionExtractor",
    "RawQuestionCandidate",
    "RuleBasedExtractor",
    "AIQuestionExtractor",
    "get_question_extractor",
]
