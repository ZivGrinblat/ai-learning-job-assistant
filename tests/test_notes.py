from app.services.note_store import (
    init_db,
    delete_note,
    save_note,
    get_all_notes,
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