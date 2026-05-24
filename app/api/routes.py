from fastapi import APIRouter

from app.schemas.text_analysis import TextAnalysisRequest
from app.services.text_analyzer import analyze_text

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@router.post("/analyze-text")
def analyze_text_endpoint(request: TextAnalysisRequest) -> dict:
    return analyze_text(request.text)
