"""
API tests for the FastAPI application.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.services.note_store import init_db


client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")

    assert response.status_code == 200


def test_health_returns_ok_status():
    response = client.get("/health")

    assert response.json() == {"status": "ok"}


def test_health_content_type_is_json():
    response = client.get("/health")

    assert response.headers["content-type"].startswith("application/json")


def test_analyze_text_endpoint_returns_analysis_for_valid_text():
    # Arrange
    payload = {"text": "Hello world"}

    # Act
    response = client.post("/analyze-text", json=payload)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "word_count": 2,
        "character_count": 11,
        "character_count_without_spaces": 10,
        "line_count": 1,
        "is_empty": False,
    }


def test_analyze_text_endpoint_returns_422_when_text_is_missing():
    # Arrange
    payload = {"message": "Hello world"}

    # Act
    response = client.post("/analyze-text", json=payload)

    # Assert
    assert response.status_code == 422

def test_clean_text_returns_cleaned_text():
    payload = {"text": "   hello     world   "}

    response = client.post("/clean-text", json=payload)

    assert response.status_code == 200
    assert response.json() == {"cleaned_text": "hello world"}

def test_analyze_text_endpoint_writes_pretty_audit_log(tmp_path, monkeypatch):
    log_file = tmp_path / "api_requests.log"
    monkeypatch.setattr("app.services.audit_logger.LOG_FILE_PATH", log_file)

    response = client.post("/analyze-text", json={"text": "Hello world"})

    assert response.status_code == 200
    log_content = log_file.read_text(encoding="utf-8")
    assert '"method": "POST"' in log_content
    assert "analyze-text" in log_content
    assert '"word_count": 2' in log_content
    assert '"status_code": 200' in log_content


def test_analyze_text_endpoint_separates_audit_log_entries(tmp_path, monkeypatch):
    log_file = tmp_path / "api_requests.log"
    monkeypatch.setattr("app.services.audit_logger.LOG_FILE_PATH", log_file)

    client.post("/analyze-text", json={"text": "One"})
    client.post("/analyze-text", json={"text": "Two"})

    log_content = log_file.read_text(encoding="utf-8")
    assert log_content.count("---") == 1


def test_health_check_does_not_write_audit_log(tmp_path, monkeypatch):
    log_file = tmp_path / "api_requests.log"
    monkeypatch.setattr("app.services.audit_logger.LOG_FILE_PATH", log_file)

    client.get("/health")

    assert not log_file.exists()


def test_get_notes_count_returns_zero_when_empty(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    
    init_db()
    
    response = client.get("/notes/count")
    
    assert response.status_code == 200
    assert response.json() == {"count": 0}
  


def test_get_notes_count_returns_three_after_posts(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))


    init_db()
    
    client.post(
        "/notes", 
        json={"book_name": "Book C", 
              "chapter_number": 1, 
              "note_text": "bla bla bla"
                  },)

    client.post(
        "/notes",
        json={"book_name": "Book A", 
              "chapter_number": 1, 
              "note_text": "note 1"
                  },)
    client.post(
        "/notes",
        json={"book_name": "Book B", 
              "chapter_number": 2, 
              "note_text": "note 2"
              },)
    
    response = client.get("/notes/count")
    assert response.status_code == 200
    assert response.json() == {"count": 3}


def test_get_notes_count_returns_several_notes_after_posts(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()
    
    client.post("/notes", json={"book_name": "Book A", 
                                "chapter_number": 1, 
                                "note_text": "bla bla bla"
                                }) 
     
    client.post("/notes", json={"book_name": "Book B", 
                                "chapter_number": 2, 
                                "note_text": "bla bla bla"
                                }) 
    client.post("/notes", json={"book_name": "Book C", 
                                "chapter_number": 5, 
                                "note_text": "bla bla bla"
                                }) 
    client.post("/notes", json={"book_name": "Book D", 
                                "chapter_number": 3, 
                                "note_text": "bla bla bla"
                                }) 
    
    
    response = client.get("/notes/count")
    assert response.status_code == 200
    assert response.json() == {"count": 4}
    
    
def test_get_notes_filters_by_book(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    
    
    init_db()
    
    client.post("/notes", json={"book_name": "Book A", 
                                "chapter_number": 1, 
                                "note_text": "bla bla bla"
                                }) 
     
    client.post("/notes", json={"book_name": "Book B", 
                                "chapter_number": 2, 
                                "note_text": "bla bla bla"
                                })
    
    
    response = client.get("/notes?book=Book A")
    
    data = response.json()
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["book"] == "Book A"
    assert data[0]["chapter"] == 1
    assert data[0]["note"] == "bla bla bla"


def test_count_for_one_book(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    
    init_db()
    
    client.post("/notes", json={"book_name": "Book A", 
                                "chapter_number": 1, 
                                "note_text": "bla bla bla"
                                }) 
     
    client.post("/notes", json={"book_name": "Book A", 
                                "chapter_number": 2, 
                                "note_text": "bla bla bla"
                                })
    
    client.post("/notes", json={"book_name": "Book B", 
                                "chapter_number": 2, 
                                "note_text": "bla bla bla"
                                })
    
    response = client.get("/notes/book-count?book=Book A")
    
    data = response.json()
    
    assert response.status_code == 200
    assert data["count"] == 2
    assert data["book"] == "Book A"


def test_get_books_returns_library_summary(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()

    client.post(
        "/notes",
        json={"book_name": "Book A", "chapter_number": 1, "note_text": "one"},
    )
    client.post(
        "/notes",
        json={"book_name": "Book A", "chapter_number": 2, "note_text": "two"},
    )
    client.post(
        "/notes",
        json={"book_name": "Book B", "chapter_number": 1, "note_text": "three"},
    )

    response = client.get("/books")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    by_name = {item["book"]: item["note_count"] for item in data}
    assert by_name["Book A"] == 2
    assert by_name["Book B"] == 1
    
    
def test_post_gc_content():
    
    response = client.post("/bio/gc-content", json={"dna_string": "ATGC"})
    
    data = response.json()
    
    assert response.status_code == 200
    assert data['length'] == 4
    assert data['gc_count'] == 2
    assert data['gc_percent'] == 50.0
    
def test_post_gc_reverse_complement():
    
    response = client.post("/bio/reverse-complement", json={"dna_string": "ATGC"})
    
    data = response.json()
    
    assert response.status_code == 200
    assert data["reverse_complement"] == "gcat"
    assert data['dna_string'] == "atgc"
    
def test_return_neucleotids_counts():
    response = client.post("/bio/nucleotide-counts", json={"dna_string": "ATGC"})
    
    data = response.json()
    
    assert response.status_code == 200
    assert data["dna_string"] == "atgc"
    assert data["a"] == 1 and data["c"] == 1 and data["g"] == 1 and data["t"] == 1
    
    
    
    
    
    