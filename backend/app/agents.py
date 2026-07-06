import os
import re
import json
from typing import Any, Dict, List, Tuple, Optional
from groq import Groq

from app.database import hybrid_retrieve, get_related_documents

# Helper to get Groq client
def get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Please add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)

# Helper to extract JSON from markdown code block if present
def extract_json(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text

# Default model on Groq
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# 1. Planner Agent
def run_planner(question: str, memory_str: str = "") -> List[str]:
    client = get_client()
    prompt = f"""You are the Planner Agent of a Product Intelligence system. 
Your task is to decompose the following business question into a list of 2 to 3 specific sub-queries/search terms. 
These terms will be run against a hybrid RAG system (combining vector similarity and keyword search) to retrieve the relevant facts.

Respond with ONLY a raw JSON array of query strings (e.g. ["query 1", "query 2"]). 
Do NOT include any markdown packaging, preamble, explanation, or tags.

Question: {question}
{memory_str}"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        max_tokens=1000,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_content = response.choices[0].message.content
    cleaned = extract_json(response_content)
    try:
        queries = json.loads(cleaned)
        if isinstance(queries, list):
            return [str(q) for q in queries]
    except Exception:
        pass
        
    # Fallback to splitting question words or using the question itself
    return [question]

# 2. Retrieval Agent
def run_retrieval(queries: List[str], max_total_docs: int = 5) -> List[Dict[str, Any]]:
    retrieved_docs = {}
    
    # 1. Query hybrid RAG
    for query in queries:
        docs = hybrid_retrieve(query, limit=2)
        for doc in docs:
            d_id = doc["doc_id"]
            if d_id not in retrieved_docs:
                retrieved_docs[d_id] = doc
                if len(retrieved_docs) >= max_total_docs:
                    break
        if len(retrieved_docs) >= max_total_docs:
            break
                
    # 2. Expand retrieval via cross-document links if we have budget left
    linked_docs = {}
    if len(retrieved_docs) < max_total_docs:
        for d_id, doc in retrieved_docs.items():
            related = get_related_documents(d_id)
            # Limit to 1 related document per query result
            for rel in related[:1]:
                r_id = rel["id"]
                if r_id not in retrieved_docs and r_id not in linked_docs:
                    linked_docs[r_id] = {
                        "doc_id": r_id,
                        "title": rel["title"],
                        "source_type": rel["source_type"],
                        "text": rel["body"],
                        "score": 0.5, # default relevance score for shared tags
                        "type": "cross_link"
                    }
                    if len(retrieved_docs) + len(linked_docs) >= max_total_docs:
                        break
            if len(retrieved_docs) + len(linked_docs) >= max_total_docs:
                break
                
    # Merge direct and linked documents
    all_docs = list(retrieved_docs.values()) + list(linked_docs.values())
    return all_docs[:max_total_docs]

# 3. Analysis Agent
def run_analysis(question: str, evidence: List[Dict[str, Any]], memory_str: str = "") -> str:
    client = get_client()
    
    # Format retrieved documents for model
    evidence_str = ""
    for i, doc in enumerate(evidence):
        evidence_str += f"\n--- Evidence Document {i+1} ---\n"
        evidence_str += f"ID: {doc['doc_id']}\n"
        evidence_str += f"Type: {doc['source_type']}\n"
        evidence_str += f"Title: {doc['title']}\n"
        evidence_str += f"Content: {doc['text']}\n"
        
    prompt = f"""You are the Analysis Agent. Analyze the following evidence to answer the user's business question.
Identify recurring complaints, compile quantitative counts if possible (e.g. '3 tickets reported slow search'), group related feedback, and rank product burden drivers.

Your response should contain a detailed summary of findings with references to document IDs.

Question: {question}
{memory_str}

Retrieved Evidence:
{evidence_str}"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        max_tokens=2000,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 4. Validation Agent
def run_validation(analysis_draft: str, evidence: List[Dict[str, Any]]) -> str:
    client = get_client()
    
    evidence_str = ""
    for i, doc in enumerate(evidence):
        evidence_str += f"\nID: {doc['doc_id']} | Title: {doc['title']} | Content: {doc['text']}\n"
        
    prompt = f"""You are the Validation Agent. 
Verify the claims in the analysis draft below strictly against the raw evidence.
If there are any assertions in the draft that are NOT supported by the evidence, remove or modify them.
Do NOT allow hallucinations or ungrounded assumptions.
Ensure that every claim in the output is fully grounded in the provided documents.

Analysis Draft:
{analysis_draft}

Raw Evidence:
{evidence_str}"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        max_tokens=2000,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 5. Report-Writer Agent
def run_report_writer(question: str, validated_facts: str, evidence: List[Dict[str, Any]], memory_str: str = "") -> str:
    client = get_client()
    
    evidence_str = "\n".join([f"- [{doc['doc_id']}] {doc['title']} ({doc['source_type']})" for doc in evidence])
    
    prompt = f"""You are the Report-Writer Agent. Synthesize the validated facts and compile a comprehensive, polished markdown report.
Use standard GitHub markdown. The report must contain the following sections:

# Executive Summary
(Summarize the core findings and context)

# Detailed Analysis & Metrics
(Provide ranked list of issues, complaints, frequencies, and insights backed by the validated facts)

# Key Dissatisfaction Drivers & Opportunities
(Highlight risks and opportunities identified in the text)

# Actionable Recommendations
(Suggest prioritized product or engineering tasks)

# Citations
(List the documents that contributed to this report)

Validated Facts:
{validated_facts}
{memory_str}

Sources available:
{evidence_str}"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        max_tokens=3000,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# End-to-End Orchestrator (Deep Research Mode)
def orchestrate_deep_research(question: str, session_id: Optional[str] = None) -> Tuple[str, List[Dict[str, Any]]]:
    from app.database import get_memory
    import time
    
    print("\n--- [START] Deep Research Orchestration ---")
    print(f"Question: '{question}'")
    if session_id:
        print(f"Session ID: '{session_id}'")
        
    start_time = time.time()
    
    # Fetch past session memory if available
    memory_str = ""
    if session_id:
        memories = get_memory(session_id)
        if memories:
            print(f"  [Memory] Loaded {len(memories)} past session memories")
            memory_str = "\n--- Past Session Memory (Key findings & facts to keep in mind) ---\n"
            for m in memories:
                memory_str += f"- [{m['type']}]: {m['content']}\n"
                
    # Step 1: Plan
    print("\n[Stage 1/5] Planner Agent: Generating sub-queries...")
    queries = run_planner(question, memory_str=memory_str)
    print(f"  Generated Sub-queries: {queries}")
    
    # Step 2: Retrieve
    print("\n[Stage 2/5] Retrieval Agent: Fetching and linking documents...")
    evidence = run_retrieval(queries)
    evidence_ids = [doc["doc_id"] for doc in evidence]
    print(f"  Retrieved {len(evidence)} documents: {evidence_ids}")
    if not evidence:
        print("  ❌ No relevant documents found.")
        return "No relevant documents or evidence were found in the knowledge base.", []
        
    # Step 3: Analyze
    print("\n[Stage 3/5] Analysis Agent: Synthesizing facts and metrics...")
    analysis_draft = run_analysis(question, evidence, memory_str=memory_str)
    print(f"  Analysis Draft length: {len(analysis_draft)} characters")
    
    # Step 4: Validate
    print("\n[Stage 4/5] Validation Agent: Cross-referencing draft against evidence...")
    validated_facts = run_validation(analysis_draft, evidence)
    print(f"  Validated Facts length: {len(validated_facts)} characters")
    
    # Step 5: Write Report
    print("\n[Stage 5/5] Report-Writer Agent: Structuring final report...")
    final_report = run_report_writer(question, validated_facts, evidence, memory_str=memory_str)
    print(f"  Report generated: {len(final_report)} characters")
    
    elapsed = time.time() - start_time
    print(f"--- [END] Deep Research Completed in {elapsed:.2f}s ---\n")
    
    return final_report, evidence
