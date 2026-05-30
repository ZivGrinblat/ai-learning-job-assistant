import sqlite3
import os

from pydantic_core.core_schema import none_schema

from app.schemas import notes

DB_PATH = "data/notes.db"

CREATE_TABLE = """CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)"""

def init_db():
    os.makedirs("data", exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute(CREATE_TABLE)
    connection.close()
    
def save_note(book: str, chapter: int, note: str):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.execute("INSERT INTO notes (book, chapter, note) VALUES (?, ?, ?)",
                       (book, chapter, note))
    new_id = cursor.lastrowid

    connection.commit()
    connection.close()
    return new_id
    
def delete_note(note_id: int):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    deleted = cursor.rowcount > 0
    connection.commit()
    connection.close()
    return deleted


def get_all_notes():
    connection = sqlite3.connect(DB_PATH)
    
    rows = connection.execute("SELECT * FROM notes").fetchall()
    connection.close()
    list_of_rows = []
    for row in rows:
        new_note = {
         "id": row[0], 
         "book": row[1], 
         "chapter": row[2], 
         "note": row[3], 
         "created_at": row[4]
        }
        list_of_rows.append(new_note)
    return list_of_rows

def get_notes_by_book_name(book_name: str):
    try:
        with sqlite3.connect(DB_PATH) as connection:
            rows = connection.execute(
                "SELECT * FROM notes WHERE book = ?",
                                     (book_name,)
                                     ).fetchall()
    except sqlite3.Error as error:
        print(f"Database error: {error}")
        return []
    
    notes = []

    for row in rows:
        notes.append({
            "id": row[0],
            "book": row[1],
            "chapter": row[2],
            "note": row[3],
            "created_at": row[4],
        })

    return notes


def get_note_by_id(note_id: int):
    try:
        with sqlite3.connect(DB_PATH) as connection:
            row = connection.execute(
                "SELECT * FROM notes WHERE id = ?",
                (note_id,)
            ).fetchone()

    except sqlite3.Error as error:
        print(f"Database error: {error}")
        return None

    if row is None:
        return None

    new_note = {
        "id": row[0],
        "book": row[1],
        "chapter": row[2],
        "note": row[3],
        "created_at": row[4],
    }

    return new_note

def count_notes() -> int | None:
    try:
        with sqlite3.connect(DB_PATH) as connection:
            number_of_notes = connection.execute("SELECT COUNT(*) FROM notes").fetchone()
            
    except sqlite3.Error as error:
        print(f"Database error: {error}")
        return None
    
    return number_of_notes[0]


def count_notes_for_one_book(book_name: str) -> int | None:
    try:
        with sqlite3.connect(DB_PATH) as connection:
            notes_count = connection.execute("SELECT COUNT(*) FROM notes WHERE book = ?", (book_name, )).fetchone()
    except sqlite3.Error as error:
        print(f"Database error: {error}")
        return None
    return notes_count[0]


def get_books():
    connection = sqlite3.connect(DB_PATH)
    rows = connection.execute(
        "SELECT book, COUNT(*) FROM notes GROUP BY book"
    ).fetchall()
    connection.close()

    list_of_books = []
    for row in rows:
        list_of_books.append({"book": row[0], "note_count": row[1]})

    return list_of_books