import sqlite3
import os

from app.schemas import notes

DB_PATH = "data/notes.db"

CREATE_TABLE = """CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sort_order INTEGER NOT NULL DEFAULT 0
)"""

SORT_CLAUSES = {
    "custom": "sort_order ASC, id ASC",
    "newest": "created_at DESC, id DESC",
    "oldest": "created_at ASC, id ASC",
    "book": "book ASC, chapter ASC, sort_order ASC",
}


def _row_to_note(row) -> dict:
    return {
        "id": row[0],
        "book": row[1],
        "chapter": row[2],
        "note": row[3],
        "created_at": row[4],
        "sort_order": row[5] if len(row) > 5 else row[0],
    }


def _ensure_schema(connection: sqlite3.Connection) -> None:
    columns = {
        row[1] for row in connection.execute("PRAGMA table_info(notes)").fetchall()
    }
    if "sort_order" not in columns:
        connection.execute(
            "ALTER TABLE notes ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"
        )
        rows = connection.execute("SELECT id FROM notes ORDER BY id").fetchall()
        for index, (note_id,) in enumerate(rows):
            connection.execute(
                "UPDATE notes SET sort_order = ? WHERE id = ?",
                (index, note_id),
            )


def init_db():
    os.makedirs("data", exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute(CREATE_TABLE)
    _ensure_schema(connection)
    connection.commit()
    connection.close()
    
def save_note(book: str, chapter: int, note: str):
    connection = sqlite3.connect(DB_PATH)
    _ensure_schema(connection)
    next_order = connection.execute(
        "SELECT COALESCE(MAX(sort_order), -1) + 1 FROM notes"
    ).fetchone()[0]
    cursor = connection.execute(
        "INSERT INTO notes (book, chapter, note, sort_order) VALUES (?, ?, ?, ?)",
        (book, chapter, note, next_order),
    )
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


def update_note(note_id: int, book: str, chapter: int, note: str) -> bool:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.execute(
        "UPDATE notes SET book = ?, chapter = ?, note = ? WHERE id = ?",
        (book, chapter, note, note_id),
    )
    updated = cursor.rowcount > 0
    connection.commit()
    connection.close()
    return updated


def reorder_notes(note_ids: list[int]) -> None:
    connection = sqlite3.connect(DB_PATH)
    for index, note_id in enumerate(note_ids):
        connection.execute(
            "UPDATE notes SET sort_order = ? WHERE id = ?",
            (index, note_id),
        )
    connection.commit()
    connection.close()


def get_notes(book_name: str | None = None, sort: str = "custom") -> list[dict]:
    order_clause = SORT_CLAUSES.get(sort, SORT_CLAUSES["custom"])

    try:
        with sqlite3.connect(DB_PATH) as connection:
            if book_name is None:
                rows = connection.execute(
                    f"SELECT * FROM notes ORDER BY {order_clause}"
                ).fetchall()
            else:
                rows = connection.execute(
                    f"SELECT * FROM notes WHERE book = ? ORDER BY {order_clause}",
                    (book_name,),
                ).fetchall()
    except sqlite3.Error as error:
        print(f"Database error: {error}")
        return []

    return [_row_to_note(row) for row in rows]


def get_all_notes():
    return get_notes()


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

    new_note = _row_to_note(row)

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