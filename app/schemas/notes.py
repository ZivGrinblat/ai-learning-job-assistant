"""
Pydantic models for the notes API.

Request models = what the client sends (validated before the route body runs).
Response models = what the client gets (documented in /docs, serialized to JSON).

Field limits here match UI constraints (e.g. note_text max 150).
"""

from pydantic import BaseModel, Field


class NoteRequest(BaseModel):
    """POST /notes body — no id; server assigns that."""

    book_name: str = Field(min_length=1, max_length=30)
    chapter_number: int = Field(gt=0)
    note_text: str = Field(min_length=1, max_length=150)


class NoteUpdateRequest(BaseModel):
    """PATCH /notes/{id} — full replacement of editable fields."""

    book_name: str = Field(min_length=1, max_length=30)
    chapter_number: int = Field(gt=0)
    note_text: str = Field(min_length=1, max_length=150)


class ReorderNotesRequest(BaseModel):
    """PUT /notes/reorder — ids in display order."""

    note_ids: list[int] = Field(min_length=1)


class NoteResponse(BaseModel):
    """Acknowledgement after create/update — includes id for client state."""

    message: str
    id: int


class NoteItem(BaseModel):
    """One note in GET /notes list — mirrors DB row shape for frontend."""

    id: int
    book: str
    chapter: int
    note: str
    created_at: str


class NoteCountResponse(BaseModel):
    count: int


class CountForOneBook(BaseModel):
    count: int = Field(gt=0)
    book: str = Field(min_length=1, max_length=30)


class BookSummary(BaseModel):
    """One row in the library sidebar."""

    book: str
    note_count: int


class BookStats(BaseModel):
    """Aggregated view for workspace header — derived from notes, not stored."""

    book: str
    note_count: int
    chapter_count: int
    last_updated: str


class SimilarBook(BaseModel):
    """Open Library search hit — title + first author."""

    title: str
    author: str
