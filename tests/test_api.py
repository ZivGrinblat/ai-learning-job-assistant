"""
API tests for app.main (FastAPI).

YOUR TURN: implement TestClient tests for GET /health.
Follow the guide in the chat — do not skip ahead.
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