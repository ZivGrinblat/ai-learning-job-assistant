from pydantic import BaseModel


class TextAnalysisRequest(BaseModel):
    text: str

class TextAnalysisResponse(BaseModel):
    word_count: int
    character_count: int
    character_count_without_spaces: int
    line_count: int
    is_empty: bool