import os
import sys
import shutil
import time
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

def verify_phase3():
    print("=== PHASE 3 RUNTIME VERIFICATION ===")
    
    # 1. Clean up existing database files
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
        t_health = time.time()
        health_resp = client.get("/health")
        print(f"Status Code: {health_resp.status_code}")
        print(f"Response: {health_resp.json()}")
        print(f"  Health Check Time: {time.time() - t_health:.2f} seconds")
        assert health_resp.status_code == 200
        assert health_resp.json()["sqlite"] == "ok"
        assert health_resp.json()["chromadb"] == "ok"
        print("  Health Check: [PASS]")
        
        # 4. Ingest Documents (1,000 documents)
        print("\n[3/5] Querying /ingest endpoint (populating 1000 documents)...")
        t_ingest = time.time()
        ingest_resp = client.post("/ingest")
        print(f"Status Code: {ingest_resp.status_code}")
        print(f"Ingested Count: {ingest_resp.json().get('ingested_count')}")
        print(f"  Ingestion Time: {time.time() - t_ingest:.2f} seconds")
        assert ingest_resp.status_code == 200
        assert ingest_resp.json().get("ingested_count") == 1000
        print("  Document Ingestion: [PASS]")
        
        # 5. Verify Memory Flow
        print("\n[4/5] Testing /memory endpoints and context injection...")
        t_mem = time.time()
        session_id = "demo-session-123"
        
        # Save memory
        memory_payload = {
            "session_id": session_id,
            "type": "preference",
            "content": "Focus recommendations specifically on search latency issues."
        }
        mem_post_resp = client.post("/memory", json=memory_payload)
        print(f"Save Memory Status: {mem_post_resp.status_code}")
        assert mem_post_resp.status_code == 200
        
        # Get memory
        mem_get_resp = client.get(f"/memory/{session_id}")
        print(f"Get Memory Status: {mem_get_resp.status_code}")
        print(f"Saved Memories: {mem_get_resp.json()}")
        assert mem_get_resp.status_code == 200
        assert len(mem_get_resp.json()) > 0
        
        # Query with session memory injected
        print("\nRunning `/query` with session memory context injection...")
        query_payload = {
            "question": "What is the primary complaint and what are your recommendations?",
            "session_id": session_id
        }
        q_resp = client.post("/query", json=query_payload)
        print(f"Status Code: {q_resp.status_code}")
        print(f"Answer (snippet): {q_resp.json().get('answer')[:350]}...")
        print(f"  Memory Workflow & Query Time: {time.time() - t_mem:.2f} seconds")
        assert q_resp.status_code == 200
        assert len(q_resp.json().get("citations")) > 0
        print("  Memory & Query Injection: [PASS]")
        
        # 6. Run Evaluation Harness
        print("\n[5/5] Executing Evaluation Harness (/evals/run)...")
        t_eval = time.time()
        eval_resp = client.post("/evals/run")
        print(f"Status Code: {eval_resp.status_code}")
        
        if eval_resp.status_code != 200:
            print(f"❌ Evals failed: {eval_resp.json()}")
            assert eval_resp.status_code == 200
            
        eval_data = eval_resp.json()
        print(f"  Evaluation Harness Time: {time.time() - t_eval:.2f} seconds")
        print("  Evaluation Harness: [PASS]")
        print("\n--- EVALUATION SUMMARY REPORT ---")
        print(f"Total Queries Run: {eval_data.get('total_queries_run')}")
        print(f"Average Retrieval Precision: {eval_data.get('average_precision')}")
        print(f"Average Retrieval Recall: {eval_data.get('average_recall')}")
        print(f"Average Answer Groundedness: {eval_data.get('average_groundedness')}")
        print("Detailed Query Results:")
        for res in eval_data.get("results", []):
            print(f" - Query: '{res.get('query')}'")
            print(f"   Precision: {res.get('precision')} | Recall: {res.get('recall')} | Groundedness: {res.get('groundedness')}")
            print(f"   Retrieved IDs: {res.get('retrieved_ids')}")
        print("---------------------------------")
        
        assert eval_data.get("total_queries_run") == 3
        
        print("\n=====================================")
        print("✔ ALL PHASE 3 VERIFICATIONS PASSED!")
        print(f"Execution Time: {time.time() - start_time:.2f} seconds")
        print("=====================================")

if __name__ == "__main__":
    # Check for GROQ_API_KEY
    if not os.environ.get("GROQ_API_KEY"):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
            
    if not os.environ.get("GROQ_API_KEY"):
        print("\n❌ ERROR: GROQ_API_KEY is not set. Please set it in your environment or a .env file.", file=sys.stderr)
        sys.exit(1)
        
    try:
        start_time = time.time()
        verify_phase3()
    except Exception as e:
        print(f"\n❌ PHASE 3 VERIFICATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)
