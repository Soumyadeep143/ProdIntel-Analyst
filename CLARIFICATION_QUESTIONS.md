# CLARIFICATION_QUESTIONS.md
### Gate 0 — Must be resolved (answered or explicitly defaulted-and-approved) before any application code is written.

The agent must present these to the user, grouped as below, and wait for answers before proceeding. Suggested defaults are given in *italics* — the agent may propose them, but must get explicit approval before relying on any of them.

## A. Data & Scope
1. What real data sources do we actually have access to for this build — real support tickets/GitHub issues/PRDs, or do we need synthetic/sample data? *(Default: generate a realistic synthetic dataset if none provided.)*
2. Approximate volume/scale to design for (hundreds vs. tens of thousands of documents)? *(Default: design for ~1,000–5,000 documents, note scalability path in architecture.)*
3. Which of the 5 question categories (Customer/Product/Engineering/Executive/Research Intelligence) are must-have for the first working version vs. nice-to-have?

## B. Models & AI Stack
4. Which LLM provider(s) should be used (Anthropic Claude, OpenAI, open-source/local models, or a mix)? *(Default: Claude via Anthropic API.)*
5. Any budget constraint on API usage during development/demo?
6. Preference for embeddings model/provider for the vector store?

## C. Architecture & Frameworks
7. Preferred agent orchestration approach/framework (e.g., LangGraph, custom orchestration, CrewAI, Anthropic's own agent SDK, or fully custom)? *(Default: custom lightweight orchestration for transparency, documented clearly.)*
8. Preferred vector database (e.g., Chroma, Pinecone, Weaviate, pgvector)? *(Default: pgvector or Chroma for easy local + cloud portability.)*
9. Preferred backend language/framework (e.g., Python + FastAPI)? *(Default: Python + FastAPI.)*
10. Should the system support incremental/streaming ingestion, or is a batch-ingest-then-query model acceptable for this deliverable? *(Default: batch ingestion is fine for v1.)*

## D. Memory
11. What should "long-term memory" persist across sessions — prior Q&A history, discovered facts/insights, user preferences, or all of the above?
12. Any specific memory backend preference (e.g., a dedicated memory store vs. reusing the vector DB with a memory namespace)?

## E. Frontend (for planning only — not built until Gate 1 clears)
13. Preferred frontend framework once we get there (e.g., React/Next.js)? *(Default: React + Vite.)*
14. Any specific UI requirements (chat interface, dashboards, report viewer, all of the above)?

## F. Deployment
15. Target deployment environment (local Docker only, or a specific cloud — AWS/GCP/Azure/Vercel/Render/Fly.io)?
16. Is a "live deployment" truly required for this submission, or is local + demo video acceptable given constraints? *(Original brief says "preferred," not mandatory.)*

## G. Timeline & Priorities
17. Is there a hard deadline for the internship deliverable?
18. Should the agent optimize for breadth (touching every capability lightly) or depth (fewer capabilities, very robust)? Evaluation criteria reward both system design and execution quality — worth aligning explicitly.

## H. Repository & Tooling
19. New repo or existing one to build into? Any required repo name/visibility (public/private)?
20. Any existing CI/CD, linting, or testing conventions to follow?

---
**Exit condition:** Every question above has a recorded answer or an explicitly approved default in `DECISIONS.md` before Phase 1 of `ROADMAP.md` begins.
