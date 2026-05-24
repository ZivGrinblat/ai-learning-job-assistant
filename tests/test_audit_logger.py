import json

from app.services import audit_logger


def test_write_api_log_writes_pretty_json(tmp_path, monkeypatch):
    log_file = tmp_path / "requests.log"
    monkeypatch.setattr(audit_logger, "LOG_FILE_PATH", log_file)

    audit_logger.write_api_log(
        method="POST",
        url="http://127.0.0.1:8000/analyze-text",
        status_code=200,
        result={"word_count": 2, "is_empty": False},
    )

    content = log_file.read_text(encoding="utf-8")
    parsed = json.loads(content)

    assert parsed["method"] == "POST"
    assert parsed["result"]["word_count"] == 2
    assert "\n  " in content


def test_write_api_log_adds_separator_between_entries(tmp_path, monkeypatch):
    log_file = tmp_path / "requests.log"
    monkeypatch.setattr(audit_logger, "LOG_FILE_PATH", log_file)

    audit_logger.write_api_log("POST", "http://example.com/a", 200, {"ok": True})
    audit_logger.write_api_log("POST", "http://example.com/b", 200, {"ok": True})

    content = log_file.read_text(encoding="utf-8")
    assert content.count("---") == 1
