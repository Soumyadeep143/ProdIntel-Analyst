from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ingest_and_retrieve_document():
    payload = {
        "documents": [
            {
                "id": "ticket-001",
                "source_type": "support_ticket",
                "title": "Search returns empty results",
                "body": "Users report that searching by product area returns no results.",
                "author": "maya",
                "created_at": "2026-05-12T10:00:00Z",
                "tags": ["search", "bug"],
                "related_ids": [],
            }
        ]
    }

    ingest_response = client.post("/ingest", json=payload)
    assert ingest_response.status_code == 200
    body = ingest_response.json()
    assert body["ingested_count"] == 1
    assert body["documents"][0]["id"] == "ticket-001"

    retrieve_response = client.get("/documents/ticket-001")
    assert retrieve_response.status_code == 200
    assert retrieve_response.json()["id"] == "ticket-001"
    assert retrieve_response.json()["source_type"] == "support_ticket"
