"""
Pydantic models for the notes API.

Request models = what the client sends (validated before the route body runs).
Response models = what the client gets (documented in /docs, serialized to JSON).

Field limits here match UI constraints (e.g. note_text max 150).
"""

from pydantic import BaseModel, Field

MAX_BOOK_NAME_LENGTH = 30
MAX_NOTE_TEXT_LENGTH = 150


class NotePayloadBase(BaseModel):
    """Shared editable note fields used by create and update operations."""

    book_name: str = Field(min_length=1, max_length=MAX_BOOK_NAME_LENGTH)
    chapter_number: int = Field(gt=0)
    note_text: str = Field(min_length=1, max_length=MAX_NOTE_TEXT_LENGTH)


class NoteRequest(NotePayloadBase):
    """POST /notes body — no id; server assigns that."""


class NoteUpdateRequest(NotePayloadBase):
    """PATCH /notes/{id} — full replacement of editable fields."""


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
    """Total notes across all books."""
    count: int


class CountForOneBook(BaseModel):
    """Notes count for a single book title."""
    count: int = Field(gt=0)
    book: str = Field(min_length=1, max_length=MAX_BOOK_NAME_LENGTH)


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
