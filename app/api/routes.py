from fastapi import APIRouter, HTTPException, Request

from app.schemas.notes import BookSummary, NoteItem, NoteRequest, NoteResponse
from app.schemas.text_analysis import TextAnalysisRequest, TextAnalysisResponse, TextCleaningRequest, TextCleaningResponse
from app.services.audit_logger import write_api_log
from app.services.text_analyzer import analyze_text, clean_text
from app.services.note_store import get_books, count_notes, get_notes_by_book_name, delete_note, get_all_notes, save_note
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


@router.post("/clean-text", response_model=TextCleaningResponse)
def clean_text_endpoint(payload: TextCleaningRequest, 
                        http_request: Request) -> TextCleaningResponse:
    result = clean_text(payload.text)
    response = TextCleaningResponse(cleaned_text=result)
    
    
    write_api_log(
        method=http_request.method,
        url=str(http_request.url),
        status_code=200,
        result=response.model_dump(),
    )
    
    return response

@router.post("/notes", response_model=NoteResponse)
def notes_endpoint(payload: NoteRequest, 
                   http_request: Request) -> NoteResponse:
    result = save_note(payload.book_name, payload.chapter_number, payload.note_text)
    response = NoteResponse(message="Note saved", id=result)
    
    
    return response

@router.get("/notes", response_model=list[NoteItem])
def get_notes_endpoint(book: str | None = None):
    if book is None:
        return get_all_notes()
    return get_notes_by_book_name(book)


@router.delete("/notes/{note_id}")
def delete_note_endpoint(note_id: int):
    deleted = delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail = "Note not found")
    return {"message": "Note deleted"}

@router.get("/notes/count", response_model=dict)
def get_count_notes():
    notes_counter = count_notes()
    return {"count": notes_counter}


@router.get("/books", response_model=list[BookSummary])
def get_books_endpoint():
    return get_books()