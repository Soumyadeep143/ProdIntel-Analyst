import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_session_memory_flow():
    # 1. Ingest clean data
    client.post("/ingest")
    
    session_id = "test-session-999"
    
    # 2. Save memory
    payload = {
        "session_id": session_id,
        "type": "preference",
        "content": "User prefers search optimization details in answers."
    }
    resp = client.post("/memory", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    
    # 3. Retrieve memory
    resp = client.get(f"/memory/{session_id}")
    assert resp.status_code == 200
    memories = resp.json()
    assert len(memories) >= 1
    assert memories[0]["session_id"] == session_id
    assert memories[0]["content"] == "User prefers search optimization details in answers."
    
    # 4. Check context injection in query
    query_payload = {
        "question": "What is the primary search issue?",
        "session_id": session_id
    }
    resp = client.post("/query", json=query_payload)
    assert resp.status_code == 200
    assert "answer" in resp.json()
    assert "citations" in resp.json()

def test_evaluation_run():
    # 1. Ingest clean data
    client.post("/ingest")
    
    # 2. Run evals endpoint
    resp = client.post("/evals/run")
    assert resp.status_code == 200
    data = resp.json()
    
    assert "total_queries_run" in data
    assert "average_precision" in data
    assert "average_recall" in data
    assert "average_groundedness" in data
    assert data["total_queries_run"] == 3
    assert len(data["results"]) == 3
