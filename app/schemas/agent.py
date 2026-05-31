"""
Pydantic models for the related-notes agent endpoint.

RelatedNotesResponse caps related at 3 — same limit enforced in note_agent.
reason is the LLM's explanation; required for research UX transparency.
"""

from pydantic import BaseModel, Field


class RelatedNoteItem(BaseModel):
    note_id: int = Field(gt=0)
    book: str = Field(min_length=1, max_length=30)
    chapter: int = Field(gt=0)
    note: str = Field(min_length=1, max_length=150)
    reason: str = Field(min_length=1, max_length=200)


class RelatedNotesResponse(BaseModel):
    source_note_id: int = Field(gt=0)
    related: list[RelatedNoteItem] = Field(max_length=3)
