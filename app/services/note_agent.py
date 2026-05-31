"""
Related-notes agent — finds up to 3 notes connected to a source note.

Uses OpenAI when OPENAI_API_KEY is set; otherwise stub (first 3 candidates).
Returns typed RelatedNotesResponse; None if source note missing (route → 404).

Depends on note_store for data — does not know HTTP.
"""

import json
import os

from openai import OpenAI

from app.schemas.agent import CreateNoteFromPromptResponse, RelatedNoteItem, RelatedNotesResponse
from app.services.note_store import get_note_by_id, get_notes

SYSTEM_PROMPT = """You are given a source note and a list of candidate notes.
Each note has id, book, chapter, and note text.

Pick up to 3 candidates most related to the source — by same book, shared topic, or similar content.
Only use IDs from the candidate list. If nothing fits, return an empty list.

Respond with JSON only:
{"related": [{"note_id": <int>, "reason": "<one short sentence>"}]}
"""


def _stub_related(others: list[dict]) -> list[RelatedNoteItem]:
    """Deterministic fallback — no API key or after OpenAI failure."""
    related = []
    for note in others[:3]:
        related.append(
            RelatedNoteItem(
                note_id=note["id"],
                book=note["book"],
                chapter=note["chapter"],
                note=note["note"],
                reason="Stub match - LLM not connected yet",
            )
        )
    return related


def _pick_related_with_openai(
    source: dict,
    others: list[dict],
    api_key: str,
) -> list[RelatedNoteItem]:
    """Ask gpt-4o-mini for ids + reasons; ignore hallucinated ids."""
    if not others:
        return []

    client = OpenAI(api_key=api_key)
    payload = {
        "source": {
            "id": source["id"],
            "book": source["book"],
            "chapter": source["chapter"],
            "note": source["note"],
        },
        "candidates": [
            {
                "id": note["id"],
                "book": note["book"],
                "chapter": note["chapter"],
                "note": note["note"],
            }
            for note in others
        ],
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    parsed = json.loads(raw)

    others_by_id = {note["id"]: note for note in others}
    related = []

    for item in parsed.get("related", [])[:3]:
        note_id = item.get("note_id")
        reason = item.get("reason", "").strip()
        note = others_by_id.get(note_id)
        if note is None or not reason:
            continue
        related.append(
            RelatedNoteItem(
                note_id=note["id"],
                book=note["book"],
                chapter=note["chapter"],
                note=note["note"],
                reason=reason[:200],
            )
        )

    return related


def find_related_notes(source_note_id: int) -> RelatedNotesResponse | None:
    """
    Load source + all other notes, pick related via OpenAI or stub.
    None means source id not found — caller maps to HTTP 404.
    """
    source = get_note_by_id(source_note_id)
    if source is None:
        return None

    all_notes = get_notes()
    others = [note for note in all_notes if note["id"] != source_note_id]

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            related = _pick_related_with_openai(source, others, api_key)
        except Exception:
            related = _stub_related(others)
    else:
        related = _stub_related(others)

    return RelatedNotesResponse(
        source_note_id=source_note_id,
        related=related,
    )
    
EXTRACT_NOTE_SYSTEM_PROMPT = """
You are given a user message about a reading note.
The message may contain a book name, chapter number, and note content.

Extract book, chapter, and note from the message.
Respond with JSON only, no other text:
{"book": "<string>", "chapter": <integer>, "note": "<string>", "ai_message": "<string>"}

Rules:
- book: max 30 characters
- chapter: integer > 0
- note: max 150 characters; summarize if needed
- ai_message: one sentence for the user explaining what you extracted; max 200 characters
- If something is unclear, make a reasonable guess and mention it in ai_message
"""

def _stub_extract_from_prompt(prompt: str) -> CreateNoteFromPromptResponse:
    
    prompt = prompt.strip()
    
    if not prompt:
        return CreateNoteFromPromptResponse(
            book= "Unknown", 
            chapter= 1,
            note= "No content",
            ai_message= "Stub preview...",
        )
    else:
        note = prompt[:150]
        return CreateNoteFromPromptResponse(
            book= "Unknown", 
            chapter= 1,
            note= note,
            ai_message= "Stub preview...",
        )

def _extract_with_openai(prompt: str, api_key: str) -> CreateNoteFromPromptResponse:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
            {"role": "system", "content": EXTRACT_NOTE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    parsed = json.loads(raw)
    
    
    return CreateNoteFromPromptResponse(
        book = str(parsed.get("book", "Unknown"))[:30],
        chapter = int(parsed.get("chapter", 1)),
        note = str(parsed.get("note", ""))[:150],
        ai_message = str(parsed.get("ai_message", "Extracted from your message."))[:200],
    )
    
def extract_note_from_prompt(prompt: str) -> CreateNoteFromPromptResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _stub_extract_from_prompt(prompt)
    else:
        try:
            return _extract_with_openai(prompt, api_key)
        except Exception:
            return _stub_extract_from_prompt(prompt)
    
        
        


