from app.services.text_analyzer import (
    count_words, 
    count_characters, 
    count_lines,
    analyze_text,
    clean_text,
)


def test_count_words_counts_two_words():
    # Arrange
    text = "Hello world"

    # Act
    result = count_words(text)

    # Assert
    assert result == 2


def test_count_words_returns_zero_for_empty_string():
    # Arrange
    text = ""

    # Act
    result = count_words(text)

    # Assert
    assert result == 0


def test_count_words_counts_one_word():
    # Arrange
    text = "hello"

    # Act
    result = count_words(text)

    # Assert
    assert result == 1


def test_count_words_counts_five_words_in_sentence():
    # Arrange
    text = "My name is Ziv Grinblat"

    # Act
    result = count_words(text)

    # Assert
    assert result == 5


def test_count_words_treats_newline_as_word_separator():
    # Arrange
    text = "My name\n Ziv Grinblat"

    # Act
    result = count_words(text)

    # Assert
    assert result == 4


def test_count_words_returns_zero_for_whitespace_only_string():
    # Arrange
    text = "     "

    # Act
    result = count_words(text)

    # Assert
    assert result == 0


def test_count_words_ignores_multiple_spaces_between_words():
    # Arrange
    text = "Hello     world"

    # Act
    result = count_words(text)

    # Assert
    assert result == 2
    
    
def test_count_characters_counts_simple_word():
    text = "hello"

    result = count_characters(text)

    assert result == 5

def test_count_characters_includes_spaces_by_default():
    text = "hello world"

    result = count_characters(text)

    assert result == 11

def test_count_characters_excludes_spaces_when_requested():
    text = "hello world"

    result = count_characters(text, include_spaces=False)

    assert result == 10

def test_count_characters_excludes_newlines_when_spaces_not_included():
    text = "hello\nworld"

    result = count_characters(text, include_spaces=False)

    assert result == 10

def test_count_characters_returns_zero_for_empty_string():
    text = ""

    result = count_characters(text)

    assert result == 0
    
    
def test_count_lines_returns_ten_for_ten_lines_in_string():
    
    text = "I\nLove\nYou\nMy\nMother\nAnd\nMy\nFather\nSo\nMuch!"
    
    result = count_lines(text)
    
    assert result == 10
    
def test_count_lines_returns_zero_for_empty_string():
    # Arrange
    text = ""

    # Act
    result = count_lines(text)

    # Assert
    assert result == 0
    
def test_count_lines_returns_zero_for_whitespace_only_string():
    # Arrange
    text = "     "

    # Act
    result = count_lines(text)

    # Assert
    assert result == 0
    
def test_count_lines_counts_single_line():
    # Arrange
    text = "hello"

    # Act
    result = count_lines(text)

    # Assert
    assert result == 1

def test_count_lines_does_not_count_trailing_newline_as_extra_line():
    # Arrange
    text = "hello\n"

    # Act
    result = count_lines(text)

    # Assert
    assert result == 1
    
def test_count_lines_counts_empty_line_between_content_lines():
    # Arrange
    text = "hello\n\nworld"

    # Act
    result = count_lines(text)

    # Assert
    assert result == 3


# --- count_words: additional edge cases ---


def test_count_words_treats_tabs_as_word_separators():
    # Arrange
    text = "hello\tworld"

    # Act
    result = count_words(text)

    # Assert
    assert result == 2


def test_count_words_ignores_leading_and_trailing_whitespace():
    # Arrange
    text = "   hello world   "

    # Act
    result = count_words(text)

    # Assert
    assert result == 2


def test_count_words_returns_zero_for_newlines_only():
    # Arrange
    text = "\n\n\t  \n"

    # Act
    result = count_words(text)

    # Assert
    assert result == 0


def test_count_words_treats_mixed_whitespace_as_separators():
    # Arrange
    text = "one \t  two\n three"

    # Act
    result = count_words(text)

    # Assert
    assert result == 3


def test_count_words_counts_hyphenated_token_as_one_word():
    # Arrange
    text = "well-known release"

    # Act
    result = count_words(text)

    # Assert
    assert result == 2


def test_count_words_counts_unicode_words():
    # Arrange
    text = "שלום עולם"

    # Act
    result = count_words(text)

    # Assert
    assert result == 2


# --- count_characters: additional edge cases ---


def test_count_characters_returns_zero_for_whitespace_only_string():
    # Arrange
    text = " \t\n "

    # Act
    result = count_characters(text)

    # Assert
    assert result == 0


def test_count_characters_counts_tabs_when_spaces_included():
    # Arrange
    text = "a\tb"

    # Act
    result = count_characters(text)

    # Assert
    assert result == 3


def test_count_characters_excludes_tabs_when_spaces_not_included():
    # Arrange
    text = "a\tb"

    # Act
    result = count_characters(text, include_spaces=False)

    # Assert
    assert result == 2


def test_count_characters_counts_emoji_as_single_characters():
    # Arrange
    text = "hi 👋"

    # Act
    result = count_characters(text)

    # Assert
    assert result == 4


def test_count_characters_excludes_multiple_spaces_when_spaces_not_included():
    # Arrange
    text = "hello     world"

    # Act
    result = count_characters(text, include_spaces=False)

    # Assert
    assert result == 10


# --- count_lines: additional edge cases ---


def test_count_lines_handles_windows_line_endings():
    # Arrange
    text = "line one\r\nline two\r\n"

    # Act
    result = count_lines(text)

    # Assert
    assert result == 2


def test_count_lines_returns_zero_for_newlines_only():
    # Arrange
    text = "\n\r\n\t\n"

    # Act
    result = count_lines(text)

    # Assert
    assert result == 0


def test_count_lines_counts_internal_blank_lines_but_not_trailing_newlines():
    # Arrange
    text = "hello\n\n\n"

    # Act
    result = count_lines(text)

    # Assert
    assert result == 3


def test_count_lines_counts_carriage_return_separated_lines():
    # Arrange
    text = "a\rb\rc"

    # Act
    result = count_lines(text)

    # Assert
    assert result == 3


def test_count_lines_treats_single_line_without_newline_as_one_line():
    # Arrange
    text = "no newline here"

    # Act
    result = count_lines(text)

    # Assert
    assert result == 1


# --- analyze_text ---

EXPECTED_ANALYZE_TEXT_KEYS = {
    "word_count",
    "character_count",
    "character_count_without_spaces",
    "line_count",
    "is_empty",
}


def test_analyze_text_returns_all_expected_keys():
    # Act
    result = analyze_text("hello")

    # Assert
    assert set(result.keys()) == EXPECTED_ANALYZE_TEXT_KEYS


def test_analyze_text_reports_stats_for_simple_sentence():
    # Arrange
    text = "Hello world"

    # Act
    result = analyze_text(text)

    # Assert
    assert result == {
        "word_count": 2,
        "character_count": 11,
        "character_count_without_spaces": 10,
        "line_count": 1,
        "is_empty": False,
    }


def test_analyze_text_returns_zeros_and_empty_flag_for_empty_string():
    # Arrange
    text = ""

    # Act
    result = analyze_text(text)

    # Assert
    assert result == {
        "word_count": 0,
        "character_count": 0,
        "character_count_without_spaces": 0,
        "line_count": 0,
        "is_empty": True,
    }


def test_analyze_text_returns_zeros_and_empty_flag_for_whitespace_only():
    # Arrange
    text = "  \t\n  "

    # Act
    result = analyze_text(text)

    # Assert
    assert result == {
        "word_count": 0,
        "character_count": 0,
        "character_count_without_spaces": 0,
        "line_count": 0,
        "is_empty": True,
    }


def test_analyze_text_marks_non_empty_for_single_word():
    # Arrange
    text = "hello"

    # Act
    result = analyze_text(text)

    # Assert
    assert result["word_count"] == 1
    assert result["is_empty"] is False


def test_analyze_text_character_count_exceeds_count_without_spaces_when_spaces_present():
    # Arrange
    text = "a b"

    # Act
    result = analyze_text(text)

    # Assert
    assert result["character_count"] == 3
    assert result["character_count_without_spaces"] == 2
    assert result["character_count"] > result["character_count_without_spaces"]


def test_analyze_text_character_counts_match_when_no_whitespace():
    # Arrange
    text = "hello"

    # Act
    result = analyze_text(text)

    # Assert
    assert result["character_count"] == 5
    assert result["character_count_without_spaces"] == 5


def test_analyze_text_reports_single_line_for_multiline_text():
    # Arrange
    text = "line one\nline two\nline three"

    # Act
    result = analyze_text(text)

    # Assert
    assert result["word_count"] == 6
    assert result["line_count"] == 1
    assert result["is_empty"] is False


def test_analyze_text_reports_zero_lines_for_newlines_only_input():
    # Arrange
    text = "\n\n"

    # Act
    result = analyze_text(text)

    # Assert
    assert result["line_count"] == 0
    assert result["word_count"] == 0
    assert result["is_empty"] is True


def test_analyze_text_handles_unicode_content():
    # Arrange
    text = "שלום עולם"

    # Act
    result = analyze_text(text)

    # Assert
    assert result["word_count"] == 2
    assert result["character_count"] == 9
    assert result["character_count_without_spaces"] == 8
    assert result["is_empty"] is False


def test_analyze_text_gets_several_lines_returns_one_line():
    # Arrange
    text = "first\r\nsecond\r\n"

    # Act
    result = analyze_text(text)

    # Assert
    assert result["word_count"] == 2
    assert result["line_count"] == 1
    assert result["is_empty"] is False


def test_analyze_text_reports_correct_counts_for_mixed_whitespace():
    # Arrange
    text = "  one \t  two\n three  "

    # Act
    result = analyze_text(text)

    # Assert
    assert result["word_count"] == 3
    assert result["line_count"] == 1
    assert result["is_empty"] is False


def test_analyze_text_includes_emoji_in_character_count():
    # Arrange
    text = "hi 👋"

    # Act
    result = analyze_text(text)

    # Assert
    assert result["word_count"] == 2
    assert result["character_count"] == 4
    assert result["character_count_without_spaces"] == 3


def test_analyze_text_counts_hyphenated_tokens_as_one_word_each():
    # Arrange
    text = "well-known release"

    # Act
    result = analyze_text(text)

    # Assert
    assert result["word_count"] == 2
    assert result["line_count"] == 1


def test_analyze_text_strips_trailing_newlines_and_counts_one_line():
    # Arrange
    text = "hello\n\n\n"

    # Act
    result = analyze_text(text)

    # Assert
    assert result["word_count"] == 1
    assert result["line_count"] == 1
    assert result["character_count"] == 5
    assert result["is_empty"] is False


def test_analyze_text_matches_counts_on_cleaned_text():
    # Arrange
    text = "Python is powerful\n\r\n\n\n\n    "

    # Act
    result = analyze_text(text)

    # Assert
    cleaned_text = clean_text(text)
    assert result == {
        "word_count": count_words(cleaned_text),
        "character_count": count_characters(cleaned_text),
        "character_count_without_spaces": count_characters(cleaned_text, include_spaces=False),
        "line_count": count_lines(cleaned_text),
        "is_empty": False,
    }
    
def test_clean_text_leading_and_trailing_spaces():
    # Arrange
    text = "  hello world   "
    
    result = clean_text(text)
    
    assert result == "hello world"
    

def test_clean_text_gets_only_spaces_returns_empty_string():
    text = "      "
    
    result = clean_text(text)
    
    assert result == "" 
    
    
def test_clean_text_multiple_lines_returns_one_line():
    text = "hello\nziv\n   ziv   "
    
    result = clean_text(text)
    
    assert result == "hello ziv ziv"
    
def test_clean_text_replaces_multiple_spaces_with_single_space():
    text = "   hello     world   "

    result = clean_text(text)

    assert result == "hello world"
    
    
