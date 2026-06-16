"""
SQLite persistence for reading notes.

All SQL lives here — routes never touch the database directly.
Returns plain dicts/lists so services and tests don't depend on Pydantic.

DB_PATH is a module constant so tests can monkeypatch to an isolated file.
"""

import os
import sqlite3

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


def _handle_db_error(error: sqlite3.Error, fallback):
    """Log a sqlite error and return a caller-provided fallback value."""
    print(f"Database error: {error}")
    return fallback


def _row_to_note(row) -> dict:
    """Convert sqlite tuple row to the dict shape NoteItem expects."""
    return {
        "id": row[0],
        "book": row[1],
        "chapter": row[2],
        "note": row[3],
        "created_at": row[4],
        "sort_order": row[5] if len(row) > 5 else row[0],
    }


def _ensure_schema(connection: sqlite3.Connection) -> None:
    """Migrate older DBs: add sort_order column and backfill from id order."""
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


def init_db() -> None:
    """Create data dir, table, and run migrations — called on app startup."""
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(CREATE_TABLE)
        _ensure_schema(connection)
        connection.commit()


def save_note(book: str, chapter: int, note: str) -> int:
    """Insert note at end of global sort_order; return new row id."""
    with sqlite3.connect(DB_PATH) as connection:
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

    return int(new_id)


def delete_note(note_id: int) -> bool:
    """Return True if a row was deleted."""
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        deleted = cursor.rowcount > 0
        connection.commit()

    return deleted


def update_note(note_id: int, book: str, chapter: int, note: str) -> bool:
    """Return True if note_id existed."""
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            "UPDATE notes SET book = ?, chapter = ?, note = ? WHERE id = ?",
            (book, chapter, note, note_id),
        )
        updated = cursor.rowcount > 0
        connection.commit()

    return updated


def reorder_notes(note_ids: list[int]) -> None:
    """Set sort_order from list index — used after drag-and-drop in UI."""
    with sqlite3.connect(DB_PATH) as connection:
        for index, note_id in enumerate(note_ids):
            connection.execute(
                "UPDATE notes SET sort_order = ? WHERE id = ?",
                (index, note_id),
            )
        connection.commit()


def get_notes(
    book_name: str | None = None,
    sort: str = "custom",
    query: str | None = None,
) -> list[dict]:
    """Filtered list; query matches note text (LIKE); sort from SORT_CLAUSES."""
    order_clause = SORT_CLAUSES.get(sort, SORT_CLAUSES["custom"])
    conditions = []
    params: list = []

    if book_name is not None:
        conditions.append("book = ?")
        params.append(book_name)

    if query:
        conditions.append("note LIKE ?")
        params.append(f"%{query}%")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    try:
        with sqlite3.connect(DB_PATH) as connection:
            rows = connection.execute(
                f"SELECT * FROM notes {where_clause} ORDER BY {order_clause}",
                params,
            ).fetchall()
    except sqlite3.Error as error:
        return _handle_db_error(error, [])

    return [_row_to_note(row) for row in rows]


def get_book_stats(book_name: str) -> dict | None:
    """Derive stats from notes; None if book has no notes (route → 404)."""
    notes = get_notes(book_name=book_name)
    if not notes:
        return None

    chapters = {note["chapter"] for note in notes}
    return {
        "book": book_name,
        "note_count": len(notes),
        "chapter_count": len(chapters),
        "last_updated": max(note["created_at"] for note in notes),
    }


def get_all_notes() -> list[dict]:
    """Unfiltered list — convenience wrapper."""
    return get_notes()


def get_note_by_id(note_id: int) -> dict | None:
    """Single note — used by note_agent and edit flows."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            row = connection.execute(
                "SELECT * FROM notes WHERE id = ?",
                (note_id,),
            ).fetchone()

    except sqlite3.Error as error:
        return _handle_db_error(error, None)

    if row is None:
        return None

    return _row_to_note(row)


def count_notes() -> int | None:
    """Total note count across all books."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            number_of_notes = connection.execute(
                "SELECT COUNT(*) FROM notes"
            ).fetchone()

    except sqlite3.Error as error:
        print(f"Database error: {error}")
        return None

    return number_of_notes[0]


def count_notes_for_one_book(book_name: str) -> int | None:
    """Count notes for a specific book title."""
    try:
        with sqlite3.connect(DB_PATH) as connection:
            notes_count = connection.execute(
                "SELECT COUNT(*) FROM notes WHERE book = ?",
                (book_name,),
            ).fetchone()
    except sqlite3.Error as error:
        return _handle_db_error(error, None)
    return notes_count[0]


def get_books() -> list[dict]:
    """Library sidebar data: GROUP BY book with counts."""
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            "SELECT book, COUNT(*) FROM notes GROUP BY book"
        ).fetchall()
    return [{"book": row[0], "note_count": row[1]} for row in rows]
