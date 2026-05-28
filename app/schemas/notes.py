from pydantic import BaseModel, Field

class NoteRequest(BaseModel):
    book_name: str = Field(min_length=1, max_length=30)
    chapter_number: int = Field(gt=0)
    note_text: str = Field(min_length=1, max_length=150)
    

class NoteResponse(BaseModel):
    message: str
    id: int
    
    
class NoteItem(BaseModel):
    id: int
    book: str
    chapter: int
    note: str
    created_at: str
    
    
class NoteCountResponse(BaseModel):
    count: int
    
class BookSummary(BaseModel):
    book: str
    note_count: int

   
class SimilarBook(BaseModel):
    title: str
    author: str

