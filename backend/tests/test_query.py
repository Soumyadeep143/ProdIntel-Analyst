from fastapi.testclient import TestClient

from app.main import app
from app.synthetic_data import generate_synthetic_documents


client = TestClient(app)


def test_query_returns_relevant_documents_with_citations():
    documents = generate_synthetic_documents(count=10)
    client.post("/ingest", json={"documents": documents})

    response = client.post(
        "/query",
        json={"question": "What complaints mention slow search latency?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert body["citations"]
    assert any("slow" in citation["text"].lower() for citation in body["citations"])
