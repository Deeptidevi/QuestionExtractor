from app.processing.answer_key_detector import AnswerKeyDetector
from app.processing.answer_matcher import AnswerMatcher
from app.processing.extractors.base import RawQuestionCandidate
from app.db.models.question import QuestionType
from app.db.models.answer import AnswerMatchStatus


def test_detect_answer_key_list_format():
    pages = [
        {
            "page_number": 3,
            "text": "Answer Key\n1 - B\n2 - C\n3 - A\n4 - D",
        }
    ]
    answers = AnswerKeyDetector.detect_answers_in_document(pages)
    assert len(answers) == 4
    assert answers[0].question_number == "1"
    assert answers[0].answer_value == "B"
    assert answers[1].question_number == "2"
    assert answers[1].answer_value == "C"


def test_detect_answer_key_grid_format():
    pages = [
        {
            "page_number": 1,
            "text": "1. A   2. C   3. B   4. D",
        }
    ]
    answers = AnswerKeyDetector.detect_answers_in_document(pages)
    assert len(answers) == 4
    assert answers[0].question_number == "1"
    assert answers[0].answer_value == "A"


def test_match_answers_uncertain_option():
    # Question has options A, B, C but answer key has 'E'
    q = RawQuestionCandidate(
        question_number="1",
        sequence_order=1,
        raw_text="1. What is X?\nA. 1\nB. 2\nC. 3",
        question_text="What is X?",
        question_type=QuestionType.MCQ,
        options=[{"label": "A", "text": "1"}, {"label": "B", "text": "2"}, {"label": "C", "text": "3"}],
        source_pages=[1],
    )
    detected = AnswerKeyDetector.detect_answers_in_document([{"page_number": 1, "text": "Answer Key\n1 - E"}])
    
    matches = AnswerMatcher.match_answers([q], detected)
    assert len(matches) == 1
    assert matches[0].match_status == AnswerMatchStatus.AMBIGUOUS
    assert matches[0].answer is None  # Should not assign ambiguous answer
    assert matches[0].warning == "ANSWER_MATCH_UNCERTAIN"
