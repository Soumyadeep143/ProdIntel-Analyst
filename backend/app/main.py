from typing import Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.synthetic_data import generate_synthetic_documents
from app.database import init_db

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Product Intelligence Analyst",
    description="Backend API for ingesting and retrieving product intelligence documents.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    # Initialize the SQLite schema and Chroma Persistent client
    init_db()


class DocumentIn(BaseModel):
    id: str
    source_type: str
    title: str
    body: str
    author: str
    created_at: str
    tags: list[str] = Field(default_factory=list)
    related_ids: list[str] = Field(default_factory=list)


class DocumentOut(DocumentIn):
    pass


class QueryRequest(BaseModel):
    question: str
    session_id: str | None = None


class Citation(BaseModel):
    id: str
    source_type: str
    title: str
    text: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]


class ResearchRequest(BaseModel):
    question: str
    session_id: str | None = None


class ResearchResponse(BaseModel):
    report_id: str
    summary: str
    citations: list[Citation]


class MemoryIn(BaseModel):
    session_id: str
    type: str = "insight"
    content: Any


# Store reports in-memory for now (memory persistence and dedicated endpoints implemented in Phase 3)
app.state.reports: dict[str, ResearchResponse] = {}


@app.get(
    "/health",
    summary="Health check",
    description="Returns the API health status and database connectivity.",
    tags=["Health"],
)
def health() -> dict[str, str]:
    from app.database import get_sqlite_conn, get_chroma_collection
    sqlite_status = "ok"
    chromadb_status = "ok"
    
    try:
        conn = get_sqlite_conn()
        conn.execute("SELECT 1")
        conn.close()
    except Exception:
        sqlite_status = "error"
        
    try:
        collection = get_chroma_collection()
        collection.count()
    except Exception:
        chromadb_status = "error"
        
    return {
        "status": "ok",
        "sqlite": sqlite_status,
        "chromadb": chromadb_status
    }


@app.post(
    "/ingest",
    summary="Ingest documents",
    description="Store documents in SQLite and document chunks in ChromaDB. Accepts a batch of documents or generates synthetic sample data when no payload is supplied.",
    tags=["Ingestion"],
)
def ingest(documents_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = documents_payload or {}
    documents_data = payload.get("documents")
    if documents_data is None:
        documents_data = generate_synthetic_documents(count=1000)

    from app.database import save_documents_bulk, ingest_documents_chunks_bulk

    save_documents_bulk(documents_data)
    ingest_documents_chunks_bulk(documents_data)

    return {
        "ingested_count": len(documents_data),
        "documents": documents_data,
    }


@app.get(
    "/documents/{document_id}",
    response_model=DocumentOut,
    summary="Get a document",
    description="Retrieve a previously ingested document by ID.",
    tags=["Documents"],
)
def get_document(document_id: str) -> DocumentOut:
    from app.database import get_document as db_get_document
    document = db_get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")
    return DocumentOut(**document)


@app.post(
    "/memory",
    summary="Save a session memory",
    description="Save a key insight or discovery associated with a session ID.",
    tags=["Memory"],
)
def save_memory_endpoint(payload: MemoryIn) -> dict[str, str]:
    from app.database import save_memory
    try:
        save_memory(payload.session_id, payload.type, payload.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save memory: {e}")
    return {"status": "ok"}


@app.get(
    "/memory/{session_id}",
    summary="Get session memory",
    description="Retrieve all saved memories for a specific session ID.",
    tags=["Memory"],
)
def get_memory_endpoint(session_id: str) -> list[dict[str, Any]]:
    from app.database import get_memory
    try:
        return get_memory(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memory: {e}")


@app.post(
    "/query",
    response_model=QueryResponse,
    summary="Query the knowledge store",
    description="Return a simple answer plus citation-backed evidence from the ingested documents.",
    tags=["Query"],
)
def query(request: QueryRequest) -> QueryResponse:
    from app.database import hybrid_retrieve, get_memory
    from app.agents import get_client
    
    try:
        docs = hybrid_retrieve(request.question, limit=4)
        if not docs:
            return QueryResponse(
                answer="No relevant documents or evidence were found in the knowledge base.",
                citations=[]
            )
            
        # Format context for Claude / Llama
        evidence_str = ""
        for i, doc in enumerate(docs):
            evidence_str += f"\n--- Document {i+1} ---\n"
            evidence_str += f"ID: {doc['doc_id']}\n"
            evidence_str += f"Title: {doc['title']}\n"
            evidence_str += f"Content: {doc['text']}\n"
            
        # Retrieve past memory findings for this session if available
        memory_str = ""
        if request.session_id:
            memories = get_memory(request.session_id)
            if memories:
                memory_str = "\n--- Past Session Memory (Key findings & facts to keep in mind) ---\n"
                for m in memories:
                    memory_str += f"- [{m['type']}]: {m['content']}\n"
            
        prompt = f"""You are a helpful assistant answering a business query.
Answer the user's question concisely using only the provided context. If the answer cannot be found in the context, say so.
Always cite the source document IDs (e.g. [support_ticket-001]) for your claims.

Question: {request.question}
{memory_str}
Context:
{evidence_str}"""

        client = get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1000,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error generating answer: {e}. However, matching evidence documents were found."
        
    citations = [
        Citation(
            id=doc["doc_id"],
            source_type=doc["source_type"],
            title=doc["title"],
            text=doc["text"]
        )
        for doc in docs
    ]
    return QueryResponse(answer=answer, citations=citations)


@app.post(
    "/research",
    response_model=ResearchResponse,
    summary="Create a research report",
    description="Create a simple structured report from the retrieved evidence.",
    tags=["Research"],
)
def research(request: ResearchRequest) -> ResearchResponse:
    from app.agents import orchestrate_deep_research
    
    try:
        report_text, evidence = orchestrate_deep_research(request.question, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deep research orchestration failed: {e}")
        
    report_id = f"report-{len(app.state.reports) + 1}"
    
    citations = [
        Citation(
            id=doc["doc_id"],
            source_type=doc["source_type"],
            title=doc["title"],
            text=doc["text"]
        )
        for doc in evidence
    ]
    
    response = ResearchResponse(
        report_id=report_id,
        summary=report_text,
        citations=citations
    )
    
    app.state.reports[report_id] = response
    return response


@app.post(
    "/evals/run",
    summary="Run evaluation harness",
    description="Run verification queries against the system, benchmarking retrieval and answer quality.",
    tags=["Evaluation"],
)
def run_evals() -> dict[str, Any]:
    from app.evals import run_evaluation
    try:
        return run_evaluation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation execution failed: {e}")
