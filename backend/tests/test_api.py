import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_guest_login():
    response = client.post("/api/auth/guest", json={"name": "Test Student"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_start_session():
    # First create student
    auth = client.post("/api/auth/guest", json={"name": "Test"})
    student_id = auth.json()["student_id"]
    
    response = client.post("/api/tutoring/start", json={
        "student_id": student_id,
        "topic": "fraction addition"
    })
    assert response.status_code == 200
    assert response.json()["type"] == "diagnostic"