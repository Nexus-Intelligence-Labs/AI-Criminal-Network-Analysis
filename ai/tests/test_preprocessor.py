from nlp.preprocessor import TextPreprocessor


def test_whitespace_normalization():

    preprocessor = TextPreprocessor()

    text = "  Rahul   Sharma\tmet\nPriya  "

    result = preprocessor.clean_text(text)

    assert result == "Rahul Sharma met Priya"


def test_unicode_normalization():

    preprocessor = TextPreprocessor()

    text = "Rahul\u00a0Sharma\tmet\nPriya"

    result = preprocessor.clean_text(text)

    assert result == "Rahul Sharma met Priya"


def test_phone_country_code_normalization():

    preprocessor = TextPreprocessor()

    text = "Contact: +91 9876543210"

    result = preprocessor.clean_text(text)

    assert result == "Contact: +919876543210"


def test_phone_hyphen_normalization():

    preprocessor = TextPreprocessor()

    text = "Contact: +91-9876543210"

    result = preprocessor.clean_text(text)

    assert result == "Contact: +919876543210"


def test_empty_text():

    preprocessor = TextPreprocessor()

    result = preprocessor.clean_text("   ")

    assert result == ""


def test_invalid_input():

    preprocessor = TextPreprocessor()

    try:
        preprocessor.clean_text(None)
        assert False
    except TypeError:
        assert True