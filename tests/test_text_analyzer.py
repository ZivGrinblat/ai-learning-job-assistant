from app.services.text_analyzer import count_words


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