from typing import Dict, List, Any
from app.database import hybrid_retrieve

EVAL_DATASET = [
    {
        "query": "What are the most common complaints about billing?",
        "gold_doc_ids": ["meeting_note-004", "meeting_note-244"],
        "expected_terms": ["billing", "invoice", "reliability", "export"]
    },
    {
        "query": "Identify complaints about latency in search.",
        "gold_doc_ids": ["support_ticket-001", "support_ticket-081", "support_ticket-201"],
        "expected_terms": ["search", "latency", "slow"]
    },
    {
        "query": "Identify billing invoice issues.",
        "gold_doc_ids": ["support_ticket-051", "support_ticket-171"],
        "expected_terms": ["billing", "invoice", "confusing"]
    }
]

def run_evaluation() -> Dict[str, Any]:
    # Import main routes locally to prevent circular import issues
    from app.main import query, QueryRequest

    results = []
    total_precision = 0.0
    total_recall = 0.0
    total_groundedness = 0.0
    
    for item in EVAL_DATASET:
        q_text = item["query"]
        gold_ids = set(item["gold_doc_ids"])
        expected = item["expected_terms"]
        
        # 1. Run hybrid retrieval (RAG)
        docs = hybrid_retrieve(q_text, limit=4)
        retrieved_ids = [d["doc_id"] for d in docs]
        
        # Calculate retrieval Precision & Recall
        intersect = set(retrieved_ids).intersection(gold_ids)
        precision = len(intersect) / len(retrieved_ids) if retrieved_ids else 0.0
        recall = len(intersect) / len(gold_ids) if gold_ids else 0.0
        
        # 2. Run Query generation (RAG LLM call)
        req = QueryRequest(question=q_text)
        resp = query(req)
        answer = resp.answer.lower()
        
        # Calculate answer groundedness score based on keyword overlap
        match_count = sum(1 for term in expected if term in answer)
        groundedness = match_count / len(expected) if expected else 0.0
        
        results.append({
            "query": q_text,
            "retrieved_ids": retrieved_ids,
            "gold_ids": list(gold_ids),
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "groundedness": round(groundedness, 2),
            "answer_preview": resp.answer[:150] + "..."
        })
        
        total_precision += precision
        total_recall += recall
        total_groundedness += groundedness
        
    n = len(EVAL_DATASET)
    return {
        "total_queries_run": n,
        "average_precision": round(total_precision / n, 2),
        "average_recall": round(total_recall / n, 2),
        "average_groundedness": round(total_groundedness / n, 2),
        "results": results
    }
