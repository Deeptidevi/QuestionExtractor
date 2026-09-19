from app.processing.extractors.rule_based import RuleBasedExtractor
from app.db.models.question import QuestionType


def test_segment_multiple_questions_with_various_numbering():
    pages = [
        {
            "page_number": 1,
            "text": (
                "1. What is 2 + 2?\nA. 3\nB. 4\nC. 5\n\n"
                "Q2. What is 3 * 3?\nA. 6\nB. 9\nC. 12\n\n"
                "Question 3: State whether True or False: Earth is round.\n(A) True\n(B) False\n\n"
                "4) Fill in the blank: The atomic number of Carbon is _____."
            ),
        }
    ]

    extractor = RuleBasedExtractor()
    questions = extractor.extract_questions(pages)

    assert len(questions) == 4
    assert questions[0].question_number == "1"
    assert questions[0].question_type == QuestionType.MCQ
    assert len(questions[0].options) == 3

    assert questions[1].question_number == "2"
    assert questions[1].question_type == QuestionType.MCQ

    assert questions[2].question_number == "3"
    assert questions[2].question_type == QuestionType.TRUE_FALSE

    assert questions[3].question_number == "4"
    assert questions[3].question_type == QuestionType.FILL_IN_THE_BLANK


def test_segment_question_spanning_multiple_pages():
    pages = [
        {
            "page_number": 1,
            "text": "1. Consider a database management system with ACID properties. Under high concurrency, explain the isolation level Serializable.",
        },
        {
            "page_number": 2,
            "text": "A. Transactions execute concurrently without any locks.\nB. Transactions appear to have executed sequentially.\nC. Only dirty reads are prevented.\nD. Non-repeatable reads are allowed.\n\n2. What is a primary key?",
        },
    ]

    extractor = RuleBasedExtractor()
    questions = extractor.extract_questions(pages)

    assert len(questions) == 2
    # Question 1 spans across pages 1 and 2
    assert questions[0].question_number == "1"
    assert questions[0].source_pages == [1, 2]
    assert len(questions[0].options) == 4
    assert questions[0].question_type == QuestionType.MCQ

    # Question 2 is only on page 2
    assert questions[1].question_number == "2"
    assert questions[1].source_pages == [2]
