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