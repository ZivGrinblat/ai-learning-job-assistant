import sqlite3
import os

CREATE_TABLE = """CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)"""

def init_db():
    os.makedirs("data", exist_ok=True)
    connection = sqlite3.connect("data/notes.db")
    connection.execute(CREATE_TABLE)
    connection.close()
    
def save_note(book: str, chapter: int, note: str):
    connection = sqlite3.connect("data/notes.db")
    connection.execute("INSERT INTO notes (book, chapter, note) VALUES (?, ?, ?)",
                       (book, chapter, note))
    connection.commit()
    connection.close()
    