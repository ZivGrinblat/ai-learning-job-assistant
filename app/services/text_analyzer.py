def count_words(text: str) -> int:
    if not text or not text.strip():
        return 0

    words = text.split()
    return len(words)