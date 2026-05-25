from pydantic import BaseModel

class NoteRequest(BaseModel):
    book_name: str
    chapter_number: int
    note_text: str

class NoteResponse(BaseModel):
    message: str
    id: int