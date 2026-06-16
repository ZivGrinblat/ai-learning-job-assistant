"""Request/response shapes for /analyze-text and /clean-text."""

from pydantic import BaseModel


class TextAnalysisRequest(BaseModel):
    """Input payload for POST /analyze-text."""
    text: str


class TextAnalysisResponse(BaseModel):
    """Computed metrics returned by POST /analyze-text."""
    word_count: int
    character_count: int
    character_count_without_spaces: int
    line_count: int
    is_empty: bool


class TextCleaningRequest(BaseModel):
    """Input payload for POST /clean-text."""
    text: str


class TextCleaningResponse(BaseModel):
    """Whitespace-normalized text returned by POST /clean-text."""
    cleaned_text: str
