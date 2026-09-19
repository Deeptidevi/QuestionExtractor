from app.processing.option_extractor import OptionExtractor


def test_extract_standard_options():
    text = (
        "What is the capital of Japan?\n"
        "A. Tokyo\n"
        "B. Kyoto\n"
        "C. Osaka\n"
        "D. Hiroshima"
    )
    stem, options = OptionExtractor.extract_options_from_block(text)
    assert stem == "What is the capital of Japan?"
    assert len(options) == 4
    assert options[0]["label"] == "A"
    assert options[0]["text"] == "Tokyo"
    assert options[1]["label"] == "B"
    assert options[1]["text"] == "Kyoto"


def test_extract_parenthesized_options():
    text = (
        "Which planet is known as the Red Planet?\n"
        "(a) Venus\n"
        "(b) Mars\n"
        "(c) Jupiter\n"
        "(d) Saturn"
    )
    stem, options = OptionExtractor.extract_options_from_block(text)
    assert stem == "Which planet is known as the Red Planet?"
    assert len(options) == 4
    assert options[0]["label"] == "A"
    assert options[1]["label"] == "B"
    assert options[1]["text"] == "Mars"


def test_extract_multiline_options():
    text = (
        "Explain the law of conservation of energy:\n"
        "A. Energy cannot be created or destroyed,\n"
        "only transformed from one form to another.\n"
        "B. Energy can be created out of nothing."
    )
    stem, options = OptionExtractor.extract_options_from_block(text)
    assert "Explain the law" in stem
    assert len(options) == 2
    assert "only transformed" in options[0]["text"]


def test_extract_inline_horizontal_options():
    text = (
        "Identify the primary color:\n"
        "A. Red   B. Orange   C. Purple   D. Brown"
    )
    stem, options = OptionExtractor.extract_options_from_block(text)
    assert "primary color" in stem
    assert len(options) == 4
    assert options[0]["text"] == "Red"
    assert options[1]["text"] == "Orange"
