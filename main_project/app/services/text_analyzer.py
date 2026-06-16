"""
Text statistics and normalization — no HTTP.

analyze_text returns a dict that TextAnalysisResponse unpacks in the route.
clean_text collapses whitespace; analyze_text runs counts on cleaned text.
"""

from typing import TypedDict


class TextAnalysisResult(TypedDict):
    word_count: int
    character_count: int
    character_count_without_spaces: int
    line_count: int
    is_empty: bool


def is_empty_or_whitespace(text: str) -> bool:
    """Return True for empty strings and whitespace-only strings."""
    return not text or not text.strip()


def count_words(text: str) -> int:
    """Count whitespace-separated tokens in text."""
    if is_empty_or_whitespace(text):
        return 0

    words = text.split()
    return len(words)


def count_characters(text: str, include_spaces: bool = True) -> int:
    """Count characters, optionally excluding all whitespace."""
    if is_empty_or_whitespace(text):
        return 0

    if include_spaces:
        return len(text)

    return len("".join(text.split()))


def count_lines(text: str) -> int:
    """Count logical lines split by newline characters."""
    if is_empty_or_whitespace(text):
        return 0

    return len(text.splitlines())


def clean_text(text: str) -> str:
    """Collapse any whitespace runs into single spaces and trim edges."""
    if is_empty_or_whitespace(text):
        return ""

    split_text = text.split()
    return " ".join(split_text)


def analyze_text(text: str) -> TextAnalysisResult:
    """Bundle all metrics for POST /analyze-text using normalized text."""
    is_empty = is_empty_or_whitespace(text)
    cleaned_text = clean_text(text)

    return {
        "word_count": count_words(cleaned_text),
        "character_count": count_characters(cleaned_text),
        "character_count_without_spaces": count_characters(
            cleaned_text, include_spaces=False
        ),
        "line_count": count_lines(cleaned_text),
        "is_empty": is_empty,
    }
