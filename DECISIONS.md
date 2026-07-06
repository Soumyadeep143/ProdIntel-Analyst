# DECISIONS.md
### Running Log of Technical & Product Decisions

Every non-delegated decision (per `AGENT.md` §6) must be added here **at the time it is made**, not reconstructed later. Format:

```
## [YYYY-MM-DD] Decision Title
- Context: why this decision was needed
- Options considered: A, B, C
- Decision: what was chosen
- Rationale: why
- Trade-offs / risks accepted
- Source: user-specified | agent-proposed-and-approved | delegated (per AGENT.md §6)
```

---

## 2026-07-06 Data Scope and Source Set
- Context: the project needed a concrete, controllable dataset for the first demo and acceptance tests.
- Options considered: real enterprise data, fully synthetic data, and mixed data.
- Decision: generate realistic synthetic data covering support tickets, GitHub issues, PRDs, meeting notes, and release notes for a few fictional product areas.
- Rationale: this keeps the build fast, controllable, and broad enough to exercise every question category cleanly.
- Trade-offs / risks accepted: the dataset will be fictional rather than real-world, so the demo is illustrative rather than production-validated.
- Source: user-specified

## 2026-07-06 Dataset Scale
- Context: the system needed a target dataset size that balances realism with iteration speed.
- Options considered: a few dozen documents, ~800–1,500 documents, and much larger corpora.
- Decision: target roughly 800–1,500 synthetic documents across all source types.
- Rationale: this is large enough to show aggregation, trend behavior, and multi-agent reasoning while keeping development and execution fast.
- Trade-offs / risks accepted: generating and indexing 800-1,500 documents locally may take a few minutes on initial startup.
- Source: user-specified

## 2026-07-06 Question Coverage Priorities
- Context: the first version needed clear demo priorities while still covering the full acceptance suite.
- Options considered: full parity across all five categories versus a core demo subset.
- Decision: Customer, Product, and Executive Intelligence are the must-have core for the demo. Engineering and Research (deep research mode) must also work, but can be slightly lighter. However, Research Intelligence must not cut corners as it showcases the multi-agent deep research capability.
- Rationale: Ensures a focused demo on core business value while demonstrating the advanced agentic capabilities of the platform.
- Trade-offs / risks accepted: Focus is shifted slightly toward reporting and multi-agent synthesis rather than detailed engineering-specific tools.
- Source: user-specified

## 2026-07-06 LLM and Reasoning Stack
- Context: the project needed a clear model provider for reasoning, generation, and agent steps.
- Options considered: Anthropic Claude, OpenAI, Groq (Llama), open-source/local models, and mixed setups.
- Decision: use Llama via the Groq API (specifically using `llama-3.3-70b-specdec` or similar models) for reasoning, generation, and agent orchestration steps.
- Rationale: it provides extremely fast inference speeds, low latency, and is cost-effective, while maintaining high reasoning capabilities.
- Trade-offs / risks accepted: the solution will depend on the Groq API rather than Anthropic.
- Source: user-specified

## 2026-07-06 Cost-Conscious Development Approach
- Context: the build needed a cost-aware development strategy.
- Options considered: unrestricted prompting, large context usage, and iterative agent loops versus cost-conscious prompting.
- Decision: keep prompts compact, cap context size, and avoid unnecessary iterative loops during development.
- Rationale: this helps the project stay practical within the requested delivery window and budget posture.
- Trade-offs / risks accepted: some complex prompts may be less exhaustive than a fully unconstrained approach.
- Source: user-specified

## 2026-07-06 Embeddings Choice
- Context: the retrieval layer needed an embeddings provider that was easy to integrate and fast to stand up locally.
- Options considered: Voyage AI embeddings, local sentence-transformers embeddings.
- Decision: Use Chroma's default local embedding function (or sentence-transformers `all-MiniLM-L6-v2`) because it is faster to get working, runs locally, and requires no additional API keys (like Voyage API key), avoiding provisioning friction.
- Rationale: Keeps the local setup robust, offline-capable, and zero-configuration.
- Trade-offs / risks accepted: Embedding quality may be slightly lower than state-of-the-art Voyage AI API, but sufficient for the dataset scale.
- Source: agent-proposed-and-approved

## 2026-07-06 Orchestration Approach
- Context: the multi-agent workflow needed a transparent implementation approach.
- Options considered: LangGraph, CrewAI, Anthropic agent SDK, and a custom lightweight orchestrator.
- Decision: use a custom lightweight orchestrator.
- Rationale: it is easier to explain in the demo and technical report, and it exposes the orchestration logic directly.
- Trade-offs / risks accepted: the implementation will be custom rather than relying on a higher-level framework.
- Source: user-specified

## 2026-07-06 Storage and Retrieval Architecture
- Context: the system needed a local-first vector store plus structured metadata support for aggregate queries.
- Options considered: Chroma with SQLite, pgvector with Postgres, and fully external managed services.
- Decision: use Chroma as the vector store and SQLite for structured metadata and aggregate queries; document pgvector/Postgres as the scaling path for later growth.
- Rationale: this keeps the local demo simple and dependency-light while still supporting the SQL-shaped questions required by the PRD.
- Trade-offs / risks accepted: the initial version will not use a full database server, though the architecture documents a migration path.
- Source: user-specified

## 2026-07-06 Backend Stack
- Context: the backend stack needed to align with the project goals and developer workflow.
- Options considered: Python + FastAPI, other Python frameworks, and non-Python stacks.
- Decision: use Python + FastAPI.
- Rationale: it is a strong fit for rapid API development, clear backend structure, and straightforward local demos.
- Trade-offs / risks accepted: the project will favor Python ergonomics over maximum ecosystem breadth in other languages.
- Source: user-specified

## 2026-07-06 Ingestion Model
- Context: the system needed a practical ingestion strategy for v1.
- Options considered: streaming ingestion and batch ingestion.
- Decision: use batch ingestion (ingest-then-query) for the first version.
- Rationale: it is simpler to build and easier to validate within the delivery timeline.
- Trade-offs / risks accepted: incremental/streaming ingestion will be deferred.
- Source: agent-proposed-and-approved

## 2026-07-06 Memory Strategy
- Context: the product needed long-term memory with a simple implementation path.
- Options considered: separate memory storage and reusing the vector store with a dedicated namespace.
- Decision: persist prior Q&A history and key findings/insights in a dedicated SQLite table / namespace separate from the document vector store, to keep memory retrieval separate from RAG retrieval.
- Rationale: keeps memory retrieval clean and isolates session history from content searches.
- Trade-offs / risks accepted: memory operations require simple relational queries rather than a high-performance vector lookup, which is ideal for the target scale.
- Source: agent-proposed-and-approved

## 2026-07-06 Frontend Scope
- Context: the frontend needed a clear scope so it would not delay backend completion.
- Options considered: full dashboard and chat UI, chat plus report viewer, and no frontend until backend is verified.
- Decision: build a chat/query interface and report viewer as must-haves; trend dashboard as stretch, only if Phases 1–3 finish early. React + Vite as the frontend framework.
- Rationale: this preserves the backend-first gate and keeps the draft deliverable focused.
- Trade-offs / risks accepted: the UI will be intentionally leaner than a full analytics portal in v1.
- Source: agent-proposed-and-approved

## 2026-07-06 Deployment Target
- Context: the project needed a deployment target that could strengthen the demo.
- Options considered: local Docker only, Render/Fly.io for the backend and Vercel for the frontend, and mixed.
- Decision: Try for live deployment (backend on Render/Fly.io, frontend on Vercel). If this creates friction or consumes too much time, fall back to local Docker + demo video.
- Rationale: A live deployment is preferred and strengthens the assessment, but is not a blocker if technical constraints arise.
- Trade-offs / risks accepted: Live deployment on free tiers may experience spin-up latency or resource constraints.
- Source: user-specified

## 2026-07-06 Timeline and Delivery Priorities
- Context: the deliverable needed a realistic execution window.
- Options considered: broad coverage across all capabilities versus deeper coverage of the core backend workflow.
- Decision: optimize for depth on ingestion, retrieval, multi-agent reasoning, memory, and API behavior, while still covering all five question categories in a lighter way under an accelerated 1-day execution timeline.
- Rationale: the core backend workflow is the highest-value part of the evaluation criteria and should receive the main effort.
- Trade-offs / risks accepted: a smaller amount of time will go into visual polish and peripheral features.
- Source: user-specified

## 2026-07-06 Repository and Tooling
- Context: the project needed a lightweight repo setup and development toolchain.
- Options considered: existing repo reuse and a new repository with standard Python tooling.
- Decision: work in the current workspace directory; use pytest for tests and ruff or black for formatting/linting. No CI/CD pipeline required.
- Rationale: this keeps the project simple and easy to share.
- Trade-offs / risks accepted: the repo will be intentionally lean rather than full enterprise-standard from day one.
- Source: agent-proposed-and-approved
