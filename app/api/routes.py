"""
HTTP layer — maps URLs and status codes to service calls.

Routes stay thin: validate via schemas, call one service, translate errors to HTTP.
No SQL, no OpenAI calls, no business rules beyond HTTP concerns (404, 422).
"""

from fastapi import APIRouter, HTTPException, Request

from app.schemas.agent import CreateNoteFromPromptRequest, CreateNoteFromPromptResponse, RelatedNotesResponse

from app.schemas.bio import (
    ComplementDnaResponse,
    ComplementRnaResponse,
    DnaRequest,
    DnaResponse,
    NeucleotidsCounts,
    RestrictionEnzymesResponse,
    RestrictionSitesRequest,
    RnaRequest,
    RestrictionsResponse,
)
from app.schemas.notes import (
    BookStats,
    BookSummary,
    CountForOneBook,
    NoteItem,
    NoteRequest,
    NoteResponse,
    NoteUpdateRequest,
    ReorderNotesRequest,
    SimilarBook,
)
from app.schemas.text_analysis import (
    TextAnalysisRequest,
    TextAnalysisResponse,
    TextCleaningRequest,
    TextCleaningResponse,
)
from app.services.audit_logger import write_api_log
from app.services.bioinformatics import (
    ENZYME_SOURCE_URL,
    calculate_gc_content,
    get_restriction_enzymes_list,
    return_neucleotids_counts,
    return_reverse_complement_dna_string,
    return_reverse_complement_rna_string,
    find_restriction_sites,
)
from app.services.booksearch import find_similar_books
from app.services.note_agent import extract_note_from_prompt, find_related_notes
from app.services.note_store import (
    count_notes,
    count_notes_for_one_book,
    delete_note,
    get_book_stats,
    get_books,
    get_notes,
    reorder_notes,
    save_note,
    update_note,
)
from app.services.text_analyzer import analyze_text, clean_text

router = APIRouter()
ALLOWED_NOTE_SORTS = {"custom", "newest", "oldest", "book"}


def _raise_422_from_value_error(error: ValueError) -> None:
    """Map service-level ValueError to HTTP 422 response."""
    raise HTTPException(status_code=422, detail=str(error)) from error


def _log_success_response(http_request: Request, response_payload: dict) -> None:
    """Write a standard success log entry for HTTP request handlers."""
    write_api_log(
        method=http_request.method,
        url=str(http_request.url),
        status_code=200,
        result=response_payload,
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@router.get("/health")
def health_check() -> dict:
    """Liveness probe — frontend status dot and deploy checks."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Text analysis (early learning endpoints + audit logging)
# ---------------------------------------------------------------------------


@router.post("/analyze-text", response_model=TextAnalysisResponse)
def analyze_text_endpoint(
    payload: TextAnalysisRequest,
    http_request: Request,
) -> TextAnalysisResponse:
    """Analyze text and return computed counters for the frontend."""
    result = analyze_text(payload.text)
    response = TextAnalysisResponse(**result)
    _log_success_response(http_request, response.model_dump())
    return response


@router.post("/clean-text", response_model=TextCleaningResponse)
def clean_text_endpoint(
    payload: TextCleaningRequest,
    http_request: Request,
) -> TextCleaningResponse:
    """Normalize whitespace and return cleaned text."""
    result = clean_text(payload.text)
    response = TextCleaningResponse(cleaned_text=result)
    _log_success_response(http_request, response.model_dump())
    return response


# ---------------------------------------------------------------------------
# Notes — CRUD, search, reorder
# ---------------------------------------------------------------------------


@router.post("/notes", response_model=NoteResponse)
def create_note_endpoint(payload: NoteRequest) -> NoteResponse:
    """Create a note; service assigns id and sort_order."""
    new_id = save_note(payload.book_name, payload.chapter_number, payload.note_text)
    return NoteResponse(message="Note saved", id=new_id)


@router.get("/notes", response_model=list[NoteItem])
def get_notes_endpoint(
    book: str | None = None,
    sort: str = "custom",
    q: str | None = None,
) -> list[NoteItem]:
    """List notes; optional book filter, text search (q), and sort mode."""
    if sort not in ALLOWED_NOTE_SORTS:
        raise HTTPException(status_code=422, detail="Invalid sort option")
    return get_notes(book_name=book, sort=sort, query=q)


@router.put("/notes/reorder")
def reorder_notes_endpoint(payload: ReorderNotesRequest) -> dict[str, str]:
    """Persist drag-and-drop order — note_ids index becomes sort_order."""
    reorder_notes(payload.note_ids)
    return {"message": "Notes reordered"}


@router.patch("/notes/{note_id}", response_model=NoteResponse)
def update_note_endpoint(note_id: int, payload: NoteUpdateRequest) -> NoteResponse:
    updated = update_note(
        note_id,
        payload.book_name,
        payload.chapter_number,
        payload.note_text,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteResponse(message="Note updated", id=note_id)


@router.delete("/notes/{note_id}")
def delete_note_endpoint(note_id: int) -> dict[str, str]:
    """Delete one note by id; return 404 when note does not exist."""
    deleted = delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted"}


@router.get("/notes/count", response_model=dict)
def get_notes_count_endpoint() -> dict[str, int | None]:
    """Total notes across all books."""
    notes_counter = count_notes()
    return {"count": notes_counter}


@router.get("/notes/book-count", response_model=CountForOneBook)
def get_book_note_count_endpoint(book: str) -> CountForOneBook:
    """Count notes for one book title."""
    note_counter = count_notes_for_one_book(book)
    return {"book": book, "count": note_counter}


# ---------------------------------------------------------------------------
# Books — library, stats, external similar titles
# ---------------------------------------------------------------------------


@router.get("/books", response_model=list[BookSummary])
def get_books_endpoint() -> list[BookSummary]:
    """Sidebar library: each book with note count."""
    return get_books()


@router.get("/books/stats", response_model=BookStats)
def get_book_stats_endpoint(book: str) -> BookStats:
    """Return aggregated stats for one book; 404 if no notes exist."""
    stats = get_book_stats(book)
    if stats is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return stats


@router.get("/books/similar", response_model=list[SimilarBook])
def get_similar_books_endpoint(book: str) -> list[SimilarBook]:
    """Proxy to Open Library — no API key required."""
    return find_similar_books(book)


# ---------------------------------------------------------------------------
# Bioinformatics — pure logic; ValueError → 422
# ---------------------------------------------------------------------------
@router.post("/bio/gc-content", response_model=DnaResponse)
def bio_gc_content_endpoint(payload: DnaRequest) -> DnaResponse:
    """Calculate GC metrics for a validated DNA string."""
    try:
        return calculate_gc_content(payload.dna_string)
    except ValueError as error:
        _raise_422_from_value_error(error)


@router.post("/bio/reverse-complement", response_model=ComplementDnaResponse)
def bio_dna_reverse_complement_endpoint(payload: DnaRequest) -> ComplementDnaResponse:
    """Return DNA reverse-complement; validation errors map to 422."""
    try:
        return return_reverse_complement_dna_string(payload.dna_string)
    except ValueError as error:
        _raise_422_from_value_error(error)


@router.post("/bio/nucleotide-counts", response_model=NeucleotidsCounts)
def bio_nucleotide_counts_endpoint(payload: DnaRequest) -> NeucleotidsCounts:
    """Return nucleotide counts using legacy response naming for compatibility."""
    try:
        return return_neucleotids_counts(payload.dna_string)
    except ValueError as error:
        _raise_422_from_value_error(error)


@router.post("/bio/rna/reverse-complement", response_model=ComplementRnaResponse)
def bio_rna_reverse_complement_endpoint(payload: RnaRequest) -> ComplementRnaResponse:
    """Return RNA reverse-complement; validation errors map to 422."""
    try:
        return return_reverse_complement_rna_string(payload.rna_string)
    except ValueError as error:
        _raise_422_from_value_error(error)


@router.get("/bio/dna/restriction-enzymes", response_model=RestrictionEnzymesResponse)
def bio_dna_restriction_enzymes_endpoint() -> RestrictionEnzymesResponse:
    """List available enzymes/patterns loaded from source dataset."""
    enzymes = get_restriction_enzymes_list()
    return RestrictionEnzymesResponse(
        source=ENZYME_SOURCE_URL,
        count=len(enzymes),
        enzymes=enzymes,
    )


@router.post("/bio/dna/restriction-sites", response_model=RestrictionsResponse)
def bio_dna_restriction_sites_endpoint(payload: RestrictionSitesRequest) -> RestrictionsResponse:
    """Return restriction-site positions for selected enzymes or full catalog."""
    try:
        sites = find_restriction_sites(payload.dna_string, payload.selected_enzymes)
        return RestrictionsResponse(dna_string=payload.dna_string.lower(), sites=sites)
    except ValueError as error:
        _raise_422_from_value_error(error)
# ---------------------------------------------------------------------------
# AI agent — related notes
# ---------------------------------------------------------------------------


@router.post("/notes/{note_id}/related", response_model=RelatedNotesResponse)
def related_notes_endpoint(note_id: int) -> RelatedNotesResponse:
    """OpenAI picks related notes; stub if no key or on failure."""
    result = find_related_notes(note_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return result

@router.post("/notes/from-prompt", response_model=CreateNoteFromPromptResponse)
def create_note_from_prompt_endpoint(payload: CreateNoteFromPromptRequest) -> CreateNoteFromPromptResponse:
    """Extract draft note fields from free-form user prompt text."""
    return extract_note_from_prompt(payload.prompt_input)
