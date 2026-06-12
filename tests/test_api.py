"""
API tests for the FastAPI application.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.agent import RelatedNoteItem, CreateNoteFromPromptResponse


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

def test_post_rna_reverse_complement():
    response = client.post("/bio/rna/reverse-complement", json={"rna_string": "AAUUGGCC"})
    data = response.json()

    assert response.status_code == 200
    assert data["reverse_complement"] == "ggccaauu"
    assert data["rna_string"] == "aauuggcc"


def test_post_rna_reverse_complement_returns_422_for_invalid_letters():
    response = client.post("/bio/rna/reverse-complement", json={"rna_string": "AAD"})

    assert response.status_code == 422


def test_get_restriction_enzymes_returns_catalog():
    response = client.get("/bio/dna/restriction-enzymes")
    data = response.json()

    assert response.status_code == 200
    assert data["count"] > 0
    assert isinstance(data["enzymes"], list)
    assert {"name", "pattern"} <= set(data["enzymes"][0].keys())


def test_post_restriction_sites_returns_positions():
    response = client.post(
        "/bio/dna/restriction-sites",
        json={
            "dna_string": "AAGAATTCTT",
            "selected_enzymes": ["EcoRI"],
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["dna_string"] == "aagaattctt"
    assert data["sites"]["EcoRI"] == [2]


def test_patch_note_updates_fields(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()

    create = client.post(
        "/notes",
        json={"book_name": "Book A", "chapter_number": 1, "note_text": "original"},
    )
    note_id = create.json()["id"]

    response = client.patch(
        f"/notes/{note_id}",
        json={"book_name": "Book B", "chapter_number": 3, "note_text": "updated"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Note updated", "id": note_id}

    notes = client.get("/notes").json()
    assert notes[0]["book"] == "Book B"
    assert notes[0]["chapter"] == 3
    assert notes[0]["note"] == "updated"


def test_patch_note_returns_404_for_missing_note(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()

    response = client.patch(
        "/notes/999",
        json={"book_name": "Book A", "chapter_number": 1, "note_text": "updated"},
    )

    assert response.status_code == 404


def test_get_notes_sorts_by_newest(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()

    client.post("/notes", json={"book_name": "Book A", "chapter_number": 1, "note_text": "first"})
    client.post("/notes", json={"book_name": "Book A", "chapter_number": 2, "note_text": "second"})

    response = client.get("/notes?sort=newest")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["chapter"] == 2


def test_reorder_notes_changes_custom_order(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()

    first = client.post("/notes", json={"book_name": "Book A", "chapter_number": 1, "note_text": "one"}).json()["id"]
    second = client.post("/notes", json={"book_name": "Book A", "chapter_number": 2, "note_text": "two"}).json()["id"]

    response = client.put("/notes/reorder", json={"note_ids": [second, first]})

    assert response.status_code == 200

    notes = client.get("/notes?sort=custom").json()
    assert [note["id"] for note in notes] == [second, first]

def test_get_related_notes_by_id(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    init_db()
    
    first_id = client.post("/notes", json={"book_name": "Book A", "chapter_number": 1, "note_text": "one"}).json()["id"]
    second_id = client.post("/notes", json={"book_name": "Book A", "chapter_number": 2, "note_text": "two"}).json()["id"]
    result = client.post(f"/notes/{second_id}/related")
    data = result.json()
    

    assert result.status_code == 200
    assert data["source_note_id"] == second_id
    assert len(data["related"]) <= 3
    assert data["related"][0]["note_id"] == first_id


def test_get_related_notes_uses_openai_when_key_set(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def fake_openai_pick(source, others, api_key):
        assert api_key == "test-key"
        note = others[0]
        return [
            RelatedNoteItem(
                note_id=note["id"],
                book=note["book"],
                chapter=note["chapter"],
                note=note["note"],
                reason="Same book and theme.",
            )
        ]

    monkeypatch.setattr(
        "app.services.note_agent._pick_related_with_openai",
        fake_openai_pick,
    )

    init_db()

    first_id = client.post("/notes", json={"book_name": "Book A", "chapter_number": 1, "note_text": "one"}).json()["id"]
    second_id = client.post("/notes", json={"book_name": "Book A", "chapter_number": 2, "note_text": "two"}).json()["id"]
    result = client.post(f"/notes/{second_id}/related")
    data = result.json()

    assert result.status_code == 200
    assert data["related"][0]["note_id"] == first_id
    assert data["related"][0]["reason"] == "Same book and theme."

def test_search_notes_by_query(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    init_db()

    client.post("/notes", json={"book_name": "Bio Book", "chapter_number": 1, "note_text": "genomics DNA"})
    client.post("/notes", json={"book_name": "Bio Book", "chapter_number": 2, "note_text": "unrelated topic"})

    response = client.get("/notes?q=genomics")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert "genomics" in data[0]["note"]


def test_book_stats_endpoint(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    init_db()

    client.post("/notes", json={"book_name": "Stats Book", "chapter_number": 1, "note_text": "one"})
    client.post("/notes", json={"book_name": "Stats Book", "chapter_number": 3, "note_text": "two"})

    response = client.get("/books/stats?book=Stats%20Book")
    data = response.json()

    assert response.status_code == 200
    assert data["note_count"] == 2
    assert data["chapter_count"] == 2
    
def test_create_note_from_prompt_endpoint(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post(
        "/notes/from-prompt",
        json={"prompt_input": "Dune chapter 3 - desert teaches"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["book"] == "Unknown"
    assert data["chapter"] == 1
    assert "Stub" in data["ai_message"]
    assert "desert" in data["note"].lower()

def test_create_note_from_prompt_when_key_set(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    def fake_extract(prompt, api_key):
        assert api_key == "test-key"
        assert "Dune" in prompt
        return CreateNoteFromPromptResponse(
            book="Dune",
            chapter=3,
            note="desert teaches",
            ai_message="Extracted from your message.",
        )
    monkeypatch.setattr(
        "app.services.note_agent._extract_with_openai",
        fake_extract,
    )
    
    response = client.post(
    "/notes/from-prompt",
    json={"prompt_input": "Dune chapter 3 - desert teaches"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["book"] == "Dune"
    assert data["chapter"] == 3
    assert "desert" in data["note"]