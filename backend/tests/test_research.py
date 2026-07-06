from fastapi.testclient import TestClient

from app.main import app
from app.synthetic_data import generate_synthetic_documents


client = TestClient(app)


def test_research_returns_structured_report():
    app.state.documents = {}
    documents = generate_synthetic_documents(count=12)
    client.post("/ingest", json={"documents": documents})

    response = client.post(
        "/research",
        json={"question": "What issues are affecting search and billing?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["report_id"]
    assert body["summary"]
    assert body["citations"]
