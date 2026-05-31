from app.schemas.agent import RelatedNoteItem, RelatedNotesResponse
from app.services.note_store import get_note_by_id, get_notes

def find_related_notes(source_note_id: int) -> RelatedNotesResponse | None:
    source = get_note_by_id(source_note_id)
    
    if source is None:
        return None
    
    all_notes = get_notes()
    
    others = [note for note in all_notes if note["id"] != source_note_id]
    
    related = []
    
    for note in others[:3]:
        related.append(RelatedNoteItem(
            note_id = note["id"],
            book = note["book"],
            chapter = note["chapter"],
            note = note["note"],
            reason = "Stub match - LLM not connected yet",
        ))    
        
    return RelatedNotesResponse(
        source_note_id=source_note_id,
        related = related,
    )