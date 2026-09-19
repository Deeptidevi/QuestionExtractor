from app.processing.confidence_engine import ConfidenceEngine
from app.db.models.question import QuestionType, ExtractionStatus


def test_confidence_high_for_well_formed_mcq():
    score = ConfidenceEngine.calculate_question_confidence(
        question_number="1",
        question_text="What is the chemical formula for table salt?",
        question_type=QuestionType.MCQ,
        options=[
            {"label": "A", "text": "NaCl"},
            {"label": "B", "text": "KCl"},
            {"label": "C", "text": "H2O"},
            {"label": "D", "text": "CO2"},
        ],
        source_pages=[1],
        ocr_confidence=0.98,
    )
    assert score.overall_score >= 0.85
    assert score.status == ExtractionStatus.SUCCESS
    assert score.review_required is False


def test_confidence_low_for_missing_number_and_few_options():
    score = ConfidenceEngine.calculate_question_confidence(
        question_number=None,
        question_text="Unnumbered fragment",
        question_type=QuestionType.MCQ,
        options=[{"label": "A", "text": "Option 1"}],
        source_pages=[1],
        ocr_confidence=0.50,
    )
    assert score.overall_score < 0.60
    assert score.status == ExtractionStatus.REVIEW_REQUIRED
    assert score.review_required is True
