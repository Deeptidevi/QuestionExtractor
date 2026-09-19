from app.processing.normalizer import Normalizer


def test_clean_text_whitespace_and_newlines():
    raw = "Question 1:   What is   photosynthesis?\r\n\r\nA.  Process   of converting light.\n\n\n\nB. Respiration."
    cleaned = Normalizer.clean_text(raw)
    assert "photosynthesis?" in cleaned
    assert "\r" not in cleaned
    assert "\n\n\n" not in cleaned


def test_clean_text_hyphenated_line_breaks():
    raw = "This is a demon-\nstration of auto-\nmated text joining."
    cleaned = Normalizer.clean_text(raw)
    assert "demonstration" in cleaned
    assert "automated" in cleaned


def test_correct_ocr_artifacts():
    # Test OCR 'l.' -> '1.'
    raw_ocr = "l. What is an algorithm?\n(0) Option D\n[A] Option A"
    corrected = Normalizer.correct_ocr_artifacts(raw_ocr)
    assert "1. What is an algorithm?" in corrected
    assert "(D) Option D" in corrected
    assert "(A) Option A" in corrected
