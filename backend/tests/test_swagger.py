from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_openapi_schema_documents_core_endpoints():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    spec = response.json()

    assert "/health" in spec["paths"]
    assert spec["paths"]["/health"]["get"]["summary"] == "Health check"
    assert spec["paths"]["/ingest"]["post"]["summary"] == "Ingest documents"
    assert spec["paths"]["/documents/{document_id}"]["get"]["summary"] == "Get a document"
