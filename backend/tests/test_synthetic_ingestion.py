from app.synthetic_data import generate_synthetic_documents


def test_generate_synthetic_documents_spans_multiple_sources():
    documents = generate_synthetic_documents(count=24)

    assert len(documents) == 24
    source_types = {document["source_type"] for document in documents}
    assert {"support_ticket", "github_issue", "prd", "meeting_note", "release_note"} <= source_types
    assert all(document["title"] for document in documents)
    assert all(document["body"] for document in documents)
