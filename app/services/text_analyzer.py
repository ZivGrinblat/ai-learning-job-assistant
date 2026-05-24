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
    cleaned_text = clean_text(text)

    return {
        "word_count": count_words(cleaned_text),
        "character_count": count_characters(cleaned_text),
        "character_count_without_spaces": count_characters(cleaned_text, include_spaces=False),
        "line_count": count_lines(cleaned_text),
        "is_empty": is_empty,
    }
    
def clean_text(text: str) -> str:
    
    if is_empty_or_whitespace(text):
        return ""
    
    splitted_text = text.split()
    return " ".join(splitted_text)

    
    