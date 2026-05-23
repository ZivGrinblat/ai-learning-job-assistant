from app.services.text_analyzer import count_words

def test_count_words_returns_zero_for_empty_string():
    assert count_words("") == 0
    
def test_count_words_returns_zero_for_spaces_only():
    assert count_words("     ") == 0


def test_count_words_counts_single_word():
    assert count_words("Python") == 1


def test_count_words_counts_multiple_words():
    assert count_words("Python is powerful") == 3


def test_count_words_ignores_extra_spaces():
    assert count_words("Python    is     powerful") == 3


def test_count_words_handles_new_lines_and_tabs():
    assert count_words("Python\nis\tpowerful") == 3