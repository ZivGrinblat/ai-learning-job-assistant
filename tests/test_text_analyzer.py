from app.services.text_analyzer import count_words, count_characters, count_lines


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