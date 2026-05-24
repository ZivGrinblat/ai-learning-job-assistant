from fastapi import APIRouter, Request

from app.schemas.text_analysis import TextAnalysisRequest, TextAnalysisResponse
from app.services.audit_logger import write_api_log
from app.services.text_analyzer import analyze_text

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@router.post("/analyze-text", response_model=TextAnalysisResponse)
def analyze_text_endpoint(
    payload: TextAnalysisRequest,
    http_request: Request,
) -> TextAnalysisResponse:
    result = analyze_text(payload.text)
    response = TextAnalysisResponse(**result)

    write_api_log(
        method=http_request.method,
        url=str(http_request.url),
        status_code=200,
        result=response.model_dump(),
    )

    return response
