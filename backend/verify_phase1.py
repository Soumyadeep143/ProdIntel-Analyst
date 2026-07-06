import os
import sys
import sqlite3
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.database import DB_PATH, get_chroma_collection, get_sqlite_conn

def verify_pipeline():
    print("=== PHASE 1 RUNTIME VERIFICATION ===")
    
    # Clean up existing database files to ensure a fresh, uncorrupted state
    import shutil
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "prodintel.db"))
    chroma_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "chroma_db"))
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Cleaned up existing DB file: {db_path}")
        except Exception as e:
            print(f"Could not clean up DB file: {e}")
            
    if os.path.exists(chroma_path):
        try:
            shutil.rmtree(chroma_path)
            print(f"Cleaned up existing Chroma directory: {chroma_path}")
        except Exception as e:
            print(f"Could not clean up Chroma directory: {e}")
            
    # 1. Initialize TestClient
    print("\n[1/6] Initializing FastAPI TestClient and DBs...")
    client = TestClient(app)
    
    # Trigger startup event explicitly to initialize tables & Chroma client
    # (TestClient automatically triggers startup event on first request or within context manager)
    with client:
        # 2. Check Health
        print("\n[2/6] Querying /health endpoint...")
        health_resp = client.get("/health")
        print(f"Status Code: {health_resp.status_code}")
        print(f"Response: {health_resp.json()}")
        assert health_resp.status_code == 200
        assert health_resp.json()["sqlite"] == "ok"
        assert health_resp.json()["chromadb"] == "ok"
        print("  Health Check: [PASS]")
        
        # 3. Check Ingestion
        print("\n[3/6] Querying /ingest endpoint (generating 1000 synthetic documents)...")
        ingest_resp = client.post("/ingest")
        print(f"Status Code: {ingest_resp.status_code}")
        ingest_data = ingest_resp.json()
        print(f"Ingested Count: {ingest_data.get('ingested_count')}")
        assert ingest_resp.status_code == 200
        assert ingest_data.get("ingested_count") == 1000
        print("  Document Ingestion: [PASS]")
        
        # 4. Check SQLite Metadata DB
        print("\n[4/6] Querying SQLite metadata DB directly...")
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        sql_count = cursor.fetchone()[0]
        print(f"Total documents in SQLite 'documents' table: {sql_count}")
        assert sql_count == 1000
        
        # Fetch one sample document
        cursor.execute("SELECT id, source_type, title, author, tags FROM documents LIMIT 1")
        sample_doc = cursor.fetchone()
        print(f"Sample Document: ID={sample_doc['id']}, Source={sample_doc['source_type']}, Title='{sample_doc['title']}', Author={sample_doc['author']}, Tags={sample_doc['tags']}")
        conn.close()
        print("  SQLite Metadata DB: [PASS]")
        
        # 5. Check ChromaDB
        print("\n[5/6] Querying ChromaDB directly...")
        collection = get_chroma_collection()
        chroma_count = collection.count()
        print(f"Total chunks in ChromaDB 'document_chunks' collection: {chroma_count}")
        assert chroma_count >= 1000  # since documents are split into chunks
        
        # Fetch sample chunks
        sample_chunks = collection.peek(limit=1)
        if sample_chunks and sample_chunks["ids"]:
            print(f"Sample Chunk: ID={sample_chunks['ids'][0]}")
            print(f"  Text: {sample_chunks['documents'][0]}")
            print(f"  Metadata: {sample_chunks['metadatas'][0]}")
        print("  ChromaDB Vector Store: [PASS]")
            
        # 6. Retrieve document via GET
        sample_id = sample_doc['id']
        print(f"\n[6/6] Retrieving sample document via GET /documents/{sample_id}...")
        get_resp = client.get(f"/documents/{sample_id}")
        print(f"Status Code: {get_resp.status_code}")
        print(f"Response (abbreviated): {get_resp.json()['title']}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == sample_id
        print("  GET Document Retrieval: [PASS]")
        
        print("\n=====================================")
        print("✔ ALL PHASE 1 VERIFICATIONS PASSED!")
        print(f"Execution Time: {time.time() - start_time:.2f} seconds")
        print("=====================================")

if __name__ == "__main__":
    import time
    try:
        start_time = time.time()
        verify_pipeline()
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)
