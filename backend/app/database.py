import os
import json
import sqlite3
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "prodintel.db")
CHROMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chroma_db")

# Helper to get SQLite connection
def get_sqlite_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize databases
def init_db() -> None:
    # 1. Initialize SQLite tables
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            author TEXT,
            created_at TEXT,
            tags TEXT,          -- JSON list
            related_ids TEXT,   -- JSON list
            session_id TEXT     -- Session association
        )
    """)
    
    # Run inline migration to add session_id if it's an existing database
    try:
        cursor.execute("ALTER TABLE documents ADD COLUMN session_id TEXT")
    except sqlite3.OperationalError:
        pass # Already altered
        
    # Memory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Clear uploaded documents on server startup to maintain temporary life cycle
    cursor.execute("DELETE FROM documents WHERE source_type LIKE 'upload_%'")
    
    conn.commit()
    conn.close()

    # 2. Initialize Chroma client & collection
    chroma_client = get_chroma_client()
    chroma_client.get_or_create_collection(name="document_chunks", embedding_function=get_embedding_function())

_chroma_client = None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _chroma_client

_embedding_function = None

def get_embedding_function():
    global _embedding_function
    if _embedding_function is None:
        import os
        if os.environ.get("RENDER") == "true" or os.environ.get("RENDER"):
            # Render free-tier is restricted to 512MB RAM. Loading the ONNX runtime library
            # spikes memory usage and triggers OOM process termination. We use a zero-RAM
            # mock embedding fallback in the cloud since SQLite keyword search performs RAG context extraction.
            class MockEmbeddingFunction:
                def __call__(self, input: list[str]) -> list[list[float]]:
                    return [[0.0] * 384 for _ in input]
            _embedding_function = MockEmbeddingFunction()
        else:
            from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
            _embedding_function = ONNXMiniLM_L6_V2()
    return _embedding_function

def get_chroma_collection():
    chroma_client = get_chroma_client()
    return chroma_client.get_or_create_collection(name="document_chunks", embedding_function=get_embedding_function())

# SQLite Operations
def save_document(doc: Dict[str, Any]) -> None:
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO documents (id, source_type, title, body, author, created_at, tags, related_ids, session_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            doc["id"],
            doc["source_type"],
            doc["title"],
            doc["body"],
            doc.get("author", ""),
            doc.get("created_at", ""),
            json.dumps(doc.get("tags", [])),
            json.dumps(doc.get("related_ids", [])),
            doc.get("session_id")
        )
    )
    conn.commit()
    conn.close()

def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    return {
        "id": row["id"],
        "source_type": row["source_type"],
        "title": row["title"],
        "body": row["body"],
        "author": row["author"],
        "created_at": row["created_at"],
        "tags": json.loads(row["tags"]) if row["tags"] else [],
        "related_ids": json.loads(row["related_ids"]) if row["related_ids"] else [],
        "session_id": row["session_id"] if "session_id" in row.keys() else None
    }

def get_all_documents() -> List[Dict[str, Any]]:
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents")
    rows = cursor.fetchall()
    conn.close()
    
    docs = []
    for row in rows:
        docs.append({
            "id": row["id"],
            "source_type": row["source_type"],
            "title": row["title"],
            "body": row["body"],
            "author": row["author"],
            "created_at": row["created_at"],
            "tags": json.loads(row["tags"]) if row["tags"] else [],
            "related_ids": json.loads(row["related_ids"]) if row["related_ids"] else []
        })
    return docs

# ChromaDB Operations (Chunking & Embeddings)
def chunk_text(text: str, chunk_size: int = 150, overlap: int = 30) -> List[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
        
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += (chunk_size - overlap)
    return chunks

def delete_document_chunks(doc_id: str) -> None:
    collection = get_chroma_collection()
    # Delete by doc_id metadata filter
    try:
        collection.delete(where={"doc_id": doc_id})
    except Exception:
        pass

def ingest_document_chunks(doc_id: str, title: str, body: str, source_type: str) -> None:
    # 1. Clean existing chunks first to ensure idempotency
    delete_document_chunks(doc_id)
    
    # 2. Chunk text
    chunks = chunk_text(body)
    
    # 3. Store in Chroma
    collection = get_chroma_collection()
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"doc_id": doc_id, "title": title, "source_type": source_type} for _ in range(len(chunks))]
    
    if chunks:
        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )

# Memory SQLite Operations
def save_memory(session_id: str, mem_type: str, content: Any) -> None:
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memory (session_id, type, content) VALUES (?, ?, ?)",
        (session_id, mem_type, json.dumps(content))
    )
    conn.commit()
    conn.close()

def get_memory(session_id: str) -> List[Dict[str, Any]]:
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memory WHERE session_id = ? ORDER BY created_at ASC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    
    memories = []
    for row in rows:
        memories.append({
            "id": row["id"],
            "session_id": row["session_id"],
            "type": row["type"],
            "content": json.loads(row["content"]),
            "created_at": row["created_at"]
        })
    return memories

# Bulk Database Operations
def save_documents_bulk(docs: List[Dict[str, Any]]) -> None:
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR REPLACE INTO documents (id, source_type, title, body, author, created_at, tags, related_ids)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                doc["id"],
                doc["source_type"],
                doc["title"],
                doc["body"],
                doc.get("author", ""),
                doc.get("created_at", ""),
                json.dumps(doc.get("tags", [])),
                json.dumps(doc.get("related_ids", []))
            )
            for doc in docs
        ]
    )
    conn.commit()
    conn.close()

def ingest_documents_chunks_bulk(docs: List[Dict[str, Any]]) -> None:
    collection = get_chroma_collection()
    
    # 1. Clean existing chunks in bulk
    doc_ids = [doc["id"] for doc in docs]
    try:
        # Chroma supports $in operator
        collection.delete(where={"doc_id": {"$in": doc_ids}})
    except Exception:
        # Fallback to individual deletes if $in fails
        for doc_id in doc_ids:
            try:
                collection.delete(where={"doc_id": doc_id})
            except Exception:
                pass

    # 2. Chunk text and collect chunks in memory
    all_chunks = []
    all_ids = []
    all_metadatas = []
    
    for doc in docs:
        doc_id = doc["id"]
        title = doc["title"]
        body = doc["body"]
        source_type = doc["source_type"]
        
        chunks = chunk_text(body)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{doc_id}_chunk_{i}")
            all_metadatas.append({
                "doc_id": doc_id,
                "title": title,
                "source_type": source_type
            })
            
    # 3. Bulk store in Chroma in batches of 400
    batch_size = 400
    for i in range(0, len(all_chunks), batch_size):
        batch_chunks = all_chunks[i:i + batch_size]
        batch_ids = all_ids[i:i + batch_size]
        batch_metadatas = all_metadatas[i:i + batch_size]
        if batch_chunks:
            # Using upsert is safer to prevent duplicate key violations
            collection.upsert(
                documents=batch_chunks,
                ids=batch_ids,
                metadatas=batch_metadatas
            )

# Hybrid Retrieval & Cross-Linking Operations
def hybrid_retrieve(
    question: str,
    limit: int = 5,
    source_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    uploaded_only: bool = False,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    # 1. Vector Search (Semantic Similarity)
    collection = get_chroma_collection()
    
    chroma_where = {}
    if source_type:
        chroma_where["source_type"] = source_type
    elif uploaded_only:
        chroma_where["source_type"] = {"$in": ["upload_txt", "upload_json", "upload_docx", "upload_pdf"]}
        if session_id:
            chroma_where["session_id"] = session_id
        
    try:
        results = collection.query(
            query_texts=[question],
            n_results=limit * 2,
            where=chroma_where if chroma_where else None
        )
    except Exception:
        results = None
        
    vector_results = []
    if results and "ids" in results and results["ids"] and results["ids"][0]:
        for idx in range(len(results["ids"][0])):
            chunk_id = results["ids"][0][idx]
            doc_text = results["documents"][0][idx]
            meta = results["metadatas"][0][idx]
            dist = results["distances"][0][idx] if "distances" in results and results["distances"] else 0.5
            
            # Simple conversion from distance (L2 or cosine) to score
            similarity = 1.0 / (1.0 + dist)
            vector_results.append({
                "chunk_id": chunk_id,
                "doc_id": meta["doc_id"],
                "title": meta["title"],
                "source_type": meta["source_type"],
                "text": doc_text,
                "score": similarity,
                "type": "vector"
            })
            
    # 2. Keyword/BM25 Search (SQLite full text / substring matching)
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    
    terms = [t.lower() for t in question.split() if t.isalnum() and len(t) > 2]
    if not terms:
        # Fallback to all split terms
        terms = [t.lower() for t in question.split() if t.isalnum()]
        
    sql_query = "SELECT * FROM documents WHERE 1=1"
    params = []
    
    if source_type:
        sql_query += " AND source_type = ?"
        params.append(source_type)
    elif uploaded_only:
        sql_query += " AND source_type LIKE 'upload_%'"
        if session_id:
            sql_query += " AND session_id = ?"
            params.append(session_id)
        
    if terms:
        like_conds = []
        for term in terms:
            like_conds.append("(title LIKE ? OR body LIKE ? OR tags LIKE ?)")
            params.extend([f"%{term}%", f"%{term}%", f"%{term}%"])
        sql_query += " AND (" + " OR ".join(like_conds) + ")"
        
    sql_query += f" LIMIT {limit * 2}"
    cursor.execute(sql_query, params)
    rows = cursor.fetchall()
    conn.close()
    
    keyword_results = []
    for row in rows:
        d_id = row["id"]
        title = row["title"]
        body = row["body"]
        s_type = row["source_type"]
        
        # Simple keyword ranking: count term overlap in combined text
        combined = f"{title} {body}".lower()
        match_count = sum(1 for term in terms if term in combined)
        score = match_count / len(terms) if terms else 0.5
        
        keyword_results.append({
            "chunk_id": f"{d_id}_chunk_0",
            "doc_id": d_id,
            "title": title,
            "source_type": s_type,
            "text": body,
            "score": score,
            "type": "keyword"
        })
        
    # 3. Reciprocal Rank Fusion (RRF) at Document Level
    merged = {}
    
    # Sort vector results by similarity score descending
    vector_results.sort(key=lambda x: x["score"], reverse=True)
    for rank, res in enumerate(vector_results):
        d_id = res["doc_id"]
        if d_id not in merged:
            merged[d_id] = {
                "doc_id": d_id,
                "title": res["title"],
                "source_type": res["source_type"],
                "text": res["text"],
                "vector_rank": rank + 1,
                "keyword_rank": None
            }
            
    # Sort keyword results by keyword score descending
    keyword_results.sort(key=lambda x: x["score"], reverse=True)
    for rank, res in enumerate(keyword_results):
        d_id = res["doc_id"]
        if d_id not in merged:
            merged[d_id] = {
                "doc_id": d_id,
                "title": res["title"],
                "source_type": res["source_type"],
                "text": res["text"],
                "vector_rank": None,
                "keyword_rank": rank + 1
            }
        else:
            merged[d_id]["keyword_rank"] = rank + 1
            
    # Rank combine
    final_results = []
    for d_id, item in merged.items():
        score = 0.0
        if item["vector_rank"] is not None:
            score += 1.0 / (60.0 + item["vector_rank"])
        if item["keyword_rank"] is not None:
            score += 1.0 / (60.0 + item["keyword_rank"])
        item["score"] = score
        final_results.append(item)
        
    # Sort by RRF score descending
    final_results.sort(key=lambda x: x["score"], reverse=True)
    
    # 4. Optional tag filter post-retrieval
    if tags:
        filtered_results = []
        for res in final_results:
            # Load doc from DB to check actual tags
            doc = get_document(res["doc_id"])
            if doc and any(t in doc["tags"] for t in tags):
                filtered_results.append(res)
        final_results = filtered_results
        
    return final_results[:limit]

def get_related_documents(doc_id: str) -> List[Dict[str, Any]]:
    doc = get_document(doc_id)
    if not doc:
        return []
        
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    
    shared_tag_docs = []
    if doc["tags"]:
        # Find other documents sharing at least one tag
        conditions = []
        params = []
        for tag in doc["tags"]:
            conditions.append("tags LIKE ?")
            params.append(f'%"{tag}"%')
            
        if conditions:
            query = "SELECT * FROM documents WHERE id != ? AND (" + " OR ".join(conditions) + ") LIMIT 3"
            params.insert(0, doc_id)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            for row in rows:
                shared_tag_docs.append({
                    "id": row["id"],
                    "source_type": row["source_type"],
                    "title": row["title"],
                    "body": row["body"],
                    "tags": json.loads(row["tags"]) if row["tags"] else [],
                    "related_ids": json.loads(row["related_ids"]) if row["related_ids"] else []
                })
                
    explicit_docs = []
    if doc["related_ids"]:
        placeholders = ",".join(["?"] * len(doc["related_ids"]))
        cursor.execute(f"SELECT * FROM documents WHERE id IN ({placeholders}) LIMIT 3", doc["related_ids"])
        rows = cursor.fetchall()
        for row in rows:
            explicit_docs.append({
                "id": row["id"],
                "source_type": row["source_type"],
                "title": row["title"],
                "body": row["body"],
                "tags": json.loads(row["tags"]) if row["tags"] else [],
                "related_ids": json.loads(row["related_ids"]) if row["related_ids"] else []
            })
            
    conn.close()
    
    # Merge and deduplicate by ID
    all_related = {}
    for item in explicit_docs:
        all_related[item["id"]] = item
    for item in shared_tag_docs:
        if item["id"] not in all_related:
            all_related[item["id"]] = item
            
    return list(all_related.values())
