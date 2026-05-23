def is_empty_or_whitespace(text: str) -> bool:
    return not text or not text.strip()


def count_words(text: str) -> int:
    if is_empty_or_whitespace(text):
        return 0

    words = text.split()
    return len(words)


def count_characters(text: str, include_spaces: bool = True) -> int:
    if is_empty_or_whitespace(text):
        return 0

    if include_spaces:
        return len(text)

    return len("".join(text.split()))


def count_lines(text: str) -> int:
    if is_empty_or_whitespace(text):
        return 0

    return len(text.splitlines())


def analyze_text(text: str) -> dict:
    is_empty = is_empty_or_whitespace(text)

    return {
        "word_count": count_words(text),
        "character_count": count_characters(text),
        "character_count_without_spaces": count_characters(text, include_spaces=False),
        "line_count": count_lines(text),
        "is_empty": is_empty,
    }