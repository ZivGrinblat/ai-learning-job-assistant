"""
API tests for the FastAPI application.
"""

from fastapi.testclient import TestClient

from app.main import app


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