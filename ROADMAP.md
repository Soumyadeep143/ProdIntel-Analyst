# ROADMAP.md
### Phased Execution Plan

Status legend: `[ ]` not started · `[~]` in progress · `[x]` done with evidence recorded

---

## Phase 0 — Clarification (Gate 0)
- [x] Present `CLARIFICATION_QUESTIONS.md` to user
- [x] Record all answers/approved defaults in `DECISIONS.md`
- [x] User sign-off to proceed

**No application code is written until this phase is checked off.**

---

## Phase 1 — Backend Foundations
- [x] Repo scaffolding, tooling, CI basics
- [x] Data schema design (documents, chunks, metadata, memory)
- [x] Ingestion pipeline for agreed data sources (synthetic or real per Gate 0)
- [x] Vector DB + relational DB setup, working locally (e.g., via Docker Compose)
- [x] Basic `/ingest` and `/health` endpoints working end-to-end

**Checkpoint:** demonstrate a document going in and being retrievable.

---

## Phase 2 — Retrieval & Agent Layer
- [x] Hybrid retrieval (vector + metadata + keyword) implemented
- [x] Cross-document linking for related entities/product areas
- [x] Planner / Retrieval / Analysis / Validation / Report-Writer agents implemented
- [x] `/query` endpoint answering direct questions with citations
- [x] `/research` endpoint running a multi-step deep-research task end-to-end

**Checkpoint:** run a representative question from each `PRD.md` §5 category through `/query` or `/research` and show cited, correct-looking output.

---

## Phase 3 — Memory, Evaluation & Backend Hardening
- [x] Long-term memory implemented and proven to persist across sessions
- [x] Eval harness (`/evals/run`) scoring retrieval + answer quality on a fixed test set
- [x] Logging/tracing across the agent pipeline
- [x] Automated tests for ingestion, retrieval, and agent pipeline pass
- [x] `BACKEND_VERIFICATION.md` written summarizing all of the above with evidence

**Gate 1 — Backend-Complete.** User reviews `BACKEND_VERIFICATION.md` and explicitly approves moving to frontend. No frontend work happens before this approval, per `AGENT.md` §5.

---

## Phase 4 — Frontend (only after Gate 1 approval)
- [x] Frontend scaffolding (framework per Gate 0 answer)
- [x] Chat/query interface wired to `/query` and `/research`
- [x] Report viewer for generated reports
- [x] Basic dashboard for trend/aggregate views (optional per Gate 0 priorities)
- [ ] End-to-end manual test: ask a question in the UI, see a cited answer

---

## Phase 5 — Deployment & Deliverables
- [x] Dockerize full stack (backend + frontend)
- [ ] Deploy live instance (if approved in Gate 0) or document local run instructions clearly
- [x] Finalize `README.md` with setup/run instructions
- [x] Write Technical Report (design decisions, trade-offs, challenges, future improvements) — can largely be assembled from `DECISIONS.md` + `ARCHITECTURE.md`
- [ ] Record demo video (10–20 min) walking through architecture + live usage
- [ ] Final repo cleanup and submission checklist review against `PRD.md` §7 deliverables

---

## Backlog / Future Improvements (not built unless explicitly pulled in)
- Multi-tenant support
- Real-time/streaming ingestion
- Advanced dashboarding / BI-style analytics
- Fine-tuned or self-hosted models
- Automated CI-based eval regression gating
