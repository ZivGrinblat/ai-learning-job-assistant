from app.services.note_store import (
    count_notes,
    get_books,
    init_db,
    delete_note,
    save_note,
    get_all_notes,
    get_notes,
    update_note,
    reorder_notes,
)
import sqlite3


def test_delete_note_returns_true_for_existing_note(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    
    init_db()
    note_id = save_note("My Book", 1, "My note")
    
    result = delete_note(note_id)
    assert result is True
    
def test_delete_note_returns_false_for_nonexistent_note(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    
    init_db()

    result = delete_note(999)

    assert result is False 
    
def test_get_all_notes_returns_saved_notes(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    
    init_db()
    note_id = save_note("My Book", 1, "My note")
    note_id = save_note("My Book", 2, "My note 2")
    list_of_notes = get_all_notes()

    assert len(list_of_notes) == 2
    
def test_save_note_stores_data(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()
    note_id = save_note("My Book", 1, "My note")

    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT * FROM notes").fetchall()
    conn.close()
    assert len(rows) == 1
    assert note_id == 1
    

def test_save_note_returns_positive_id(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"

    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()

    note_id = save_note("The Muslim Jesus", 3, "First test note")

    assert note_id > 0

def test_count_notes_returns_correct_number(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    
    
    init_db()
    
    save_note("Book A", 1, "note 1")
    save_note("Book B", 2, "note 2")
    
    count = count_notes()
    
    assert count == 2
    
def test_count_notes_returns_zero_when_empty(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    
    
    init_db()   
    count = count_notes()
    
    assert count == 0


def test_get_books_returns_unique_books_with_counts(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()
    save_note("Book A", 1, "note 1")
    save_note("Book A", 2, "note 2")
    save_note("Book B", 1, "note 3")

    books = get_books()

    assert len(books) == 2
    by_name = {b["book"]: b["note_count"] for b in books}
    assert by_name["Book A"] == 2
    assert by_name["Book B"] == 1


def test_update_note_changes_fields(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()
    note_id = save_note("Book A", 1, "original")

    updated = update_note(note_id, "Book B", 4, "changed")

    assert updated is True
    note = get_notes()[0]
    assert note["book"] == "Book B"
    assert note["chapter"] == 4
    assert note["note"] == "changed"


def test_reorder_notes_updates_sort_order(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()
    first = save_note("Book A", 1, "one")
    second = save_note("Book A", 2, "two")

    reorder_notes([second, first])

    notes = get_notes(sort="custom")
    assert [note["id"] for note in notes] == [second, first]