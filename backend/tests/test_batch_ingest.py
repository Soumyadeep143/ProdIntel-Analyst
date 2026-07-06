from fastapi.testclient import TestClient

from app.main import app
from app.synthetic_data import generate_synthetic_documents


client = TestClient(app)


def test_batch_ingest_accepts_generated_documents():
    documents = generate_synthetic_documents(count=8)
    response = client.post("/ingest", json={"documents": documents})

    assert response.status_code == 200
    body = response.json()
    assert body["ingested_count"] == 8
    assert body["documents"][0]["source_type"] in {
        "support_ticket",
        "github_issue",
        "prd",
        "meeting_note",
        "release_note",
    }
