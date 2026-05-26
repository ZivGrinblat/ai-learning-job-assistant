import sqlite3
import os

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