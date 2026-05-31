import json
import os

from openai import OpenAI

from app.schemas.agent import RelatedNoteItem, RelatedNotesResponse
from app.services.note_store import get_note_by_id, get_notes

SYSTEM_PROMPT = """You are given a source note and a list of candidate notes.
Each note has id, book, chapter, and note text.

Pick up to 3 candidates most related to the source — by same book, shared topic, or similar content.
Only use IDs from the candidate list. If nothing fits, return an empty list.

Respond with JSON only:
{"related": [{"note_id": <int>, "reason": "<one short sentence>"}]}
"""


def _stub_related(others: list[dict]) -> list[RelatedNoteItem]:
    related = []
    for note in others[:3]:
        related.append(RelatedNoteItem(
            note_id=note["id"],
            book=note["book"],
            chapter=note["chapter"],
            note=note["note"],
            reason="Stub match - LLM not connected yet",
        ))
    return related


def _pick_related_with_openai(
    source: dict,
    others: list[dict],
    api_key: str,
) -> list[RelatedNoteItem]:
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
        related.append(RelatedNoteItem(
            note_id=note["id"],
            book=note["book"],
            chapter=note["chapter"],
            note=note["note"],
            reason=reason[:200],
        ))

    return related


def find_related_notes(source_note_id: int) -> RelatedNotesResponse | None:
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
