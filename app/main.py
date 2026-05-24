from fastapi import FastAPI
from pydantic import BaseModel

from app.services.text_analyzer import analyze_text


class TextAnalysisRequest(BaseModel):
    text: str


app = FastAPI(
    title="AI Learning & Job Assistant",
    description="A backend API for text analysis, learning support, and job assistance.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/analyze-text")
def analyze_text_endpoint(request: TextAnalysisRequest) -> dict:
    return analyze_text(request.text)