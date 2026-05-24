from pydantic import BaseModel


class TextAnalysisRequest(BaseModel):
    text: str
