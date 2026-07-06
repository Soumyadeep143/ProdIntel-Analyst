import os
import sys
import shutil
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

def verify_phase2():
    print("=== PHASE 2 RUNTIME VERIFICATION ===")
    
    # 1. Clean up existing database files to ensure a fresh, uncorrupted state
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

    # 2. Initialize TestClient
    print("\n[1/5] Initializing FastAPI TestClient and DBs...")
    client = TestClient(app)
    
    with client:
        # 3. Check Health
        print("\n[2/5] Querying /health endpoint...")
        health_resp = client.get("/health")
        print(f"Status Code: {health_resp.status_code}")
        print(f"Response: {health_resp.json()}")
        assert health_resp.status_code == 200
        assert health_resp.json()["sqlite"] == "ok"
        assert health_resp.json()["chromadb"] == "ok"
        print("  Health Check: [PASS]")
        
        # 4. Ingest Documents (1,000 documents)
        print("\n[3/5] Querying /ingest endpoint (populating 1000 documents)...")
        ingest_resp = client.post("/ingest")
        print(f"Status Code: {ingest_resp.status_code}")
        print(f"Ingested Count: {ingest_resp.json().get('ingested_count')}")
        assert ingest_resp.status_code == 200
        assert ingest_resp.json().get("ingested_count") == 1000
        print("  Document Ingestion: [PASS]")
        
        # 5. Query Endpoint Checks (Claude + Hybrid Retrieval)
        test_queries = [
            "What are the most common complaints about billing?",
            "Identify complaints about latency in search.",
            "Rank the major dissatisfaction drivers."
        ]
        
        print("\n[4/5] Testing /query endpoint with business questions...")
        for q in test_queries:
            print(f"\nQuerying: '{q}'")
            resp = client.post("/query", json={"question": q})
            print(f"Status Code: {resp.status_code}")
            data = resp.json()
            answer = data.get("answer")
            citations = data.get("citations", [])
            print(f"Answer (snippet): {answer[:150]}...")
            print(f"Citations returned: {len(citations)}")
            assert resp.status_code == 200
            assert len(answer) > 0
            assert len(citations) > 0
            # Print sample citation
            print(f"  Sample Citation: ID={citations[0]['id']}, Title='{citations[0]['title']}'")
        print("  Query Workflow: [PASS]")
            
        # 6. Research Endpoint Check (Multi-Agent Deep Research Loop)
        research_query = "Analyze billing complaints and write a report detailing issues and recommendations"
        print(f"\n[5/5] Testing /research endpoint (Planner -> Retrieval -> Analysis -> Validation -> Report)...")
        print(f"Research Query: '{research_query}'")
        resp = client.post("/research", json={"question": research_query})
        print(f"Status Code: {resp.status_code}")
        data = resp.json()
        if resp.status_code != 200:
            print(f"❌ Error Detail: {data}")
            assert resp.status_code == 200
            
        report_id = data.get("report_id")
        summary = data.get("summary")
        citations = data.get("citations", [])
        print("  Research Report Generation: [PASS]")
        
        print(f"Report ID: {report_id}")
        print(f"Citations returned: {len(citations)}")
        print("\n--- GENERATED REPORT SUMMARY ---")
        if summary:
            print(summary[:600])
        else:
            print("No report summary generated.")
        print("... (truncated) ...")
        print("--------------------------------")
        
        assert report_id is not None
        assert len(summary) > 0
        assert len(citations) > 0
        
        print("\n=====================================")
        print("✔ ALL PHASE 2 VERIFICATIONS PASSED!")
        print(f"Execution Time: {time.time() - start_time:.2f} seconds")
        print("=====================================")

if __name__ == "__main__":
    # Check for GROQ_API_KEY
    if not os.environ.get("GROQ_API_KEY"):
        # Load .env if present
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
            
    if not os.environ.get("GROQ_API_KEY"):
        print("\n❌ ERROR: GROQ_API_KEY is not set. Please set it in your environment or a .env file.", file=sys.stderr)
        sys.exit(1)
        
    try:
        import time
        start_time = time.time()
        verify_phase2()
    except Exception as e:
        print(f"\n❌ PHASE 2 VERIFICATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)
