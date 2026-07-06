# OUTCOME.md
### Final Certification Checklist — Autonomous Product Intelligence & Decision Support System

> **Read this file last.** It is checked only after `PROMPT.md` Phase 5 reports complete. The project is "done" only when every checkbox below is checked **with corresponding evidence in the repo** — a checkbox with no evidence is not a pass. This file itself is never edited during the build; it is only checked against, per `PROMPT.md` §4.

Status legend: `[ ]` not verified · `[x]` verified with evidence (cite the evidence location inline, e.g. *"see `BACKEND_VERIFICATION.md` §3"*)

---

## A. Process Compliance (`AGENT.md` adherence)

- [ ] No functional/product code was written before Gate 0 was cleared and recorded in `DECISIONS.md`.
- [ ] No frontend code, scaffolding, or dependency install occurred before `BACKEND_VERIFICATION.md` was reviewed and Gate 1 was explicitly approved.
- [ ] Every non-delegated decision (i.e., everything outside `AGENT.md` §6's delegated list) is logged in `DECISIONS.md` with context, options considered, decision, rationale, trade-offs, and source.
- [ ] Every phase completion claimed in `ROADMAP.md` is backed by runnable evidence (test output, curl call, or log), not just a checked box.
- [ ] All synthetic/mocked data is clearly labeled `MOCK`/`SYNTHETIC` in code, fixtures, logs, and the README.
- [ ] Any process violation that occurred was disclosed to the user with a remediation, not silently left uncorrected.

## B. Data & Ingestion

- [ ] Synthetic datasets exist for all locked-in source types: support tickets, GitHub issues, PRDs, meeting notes, release notes (interviews/competitor reports if in scope per Gate 0).
- [ ] Document/chunk counts are documented (see `BACKEND_VERIFICATION.md` §1).
- [ ] A sample record is shown end-to-end: raw → parsed → chunked → embedded → stored.
- [ ] Ingestion is idempotent/batchable as described in `ARCHITECTURE.md` §5 (documented even if not load-tested).

## C. Retrieval (RAG)

- [ ] Hybrid retrieval (vector similarity via Chroma + SQLite metadata filters + keyword/BM25 fallback) is implemented and demonstrably used, not just vector-only.
- [ ] Cross-document linking across shared entities (feature names, product areas) is demonstrated on at least one example.
- [ ] Every retrieved chunk carries a source citation through to the final answer.
- [ ] Test queries drawn from `PRD.md` §5 return relevant, cited results (see `BACKEND_VERIFICATION.md` §2).

## D. Agentic Workflow

- [ ] Planner, Retrieval, Analysis, Validation, and Report-Writer agents are all implemented and distinguishable in logs/traces (not collapsed into one undifferentiated LLM call).
- [ ] `/query` produces a direct, evidence-backed, cited answer for a representative question.
- [ ] `/research` runs a genuine multi-step, multi-pass task end-to-end and produces a structured report with citations — not a single-pass answer relabeled as "research."
- [ ] At least one full example transcript of a `/research` run (input → agent trace → final report) exists in `BACKEND_VERIFICATION.md` or the repo.

## E. Long-Term Memory

- [ ] Memory persists across two separate sessions/requests, proven with an actual test (session A stores a finding, session B recalls it) — not just code review or a design description.
- [ ] What the memory stores matches what was agreed in Gate 0 (§2.2 of `PROMPT.md`): at minimum Q&A history and discovered findings.

## F. API Contract Coverage

| Endpoint | Implemented | Tested via curl/Postman | Documented (OpenAPI/Swagger) |
|---|---|---|---|
| `/ingest` | [ ] | [ ] | [ ] |
| `/query` | [ ] | [ ] | [ ] |
| `/research` | [ ] | [ ] | [ ] |
| `/reports/{id}` | [ ] | [ ] | [ ] |
| `/memory` | [ ] | [ ] | [ ] |
| `/evals/run` | [ ] | [ ] | [ ] |
| `/health` | [ ] | [ ] | [ ] |

## G. Evaluation & Observability

- [ ] A minimal eval harness exists and runs against a fixed test set derived from `PRD.md` §5.
- [ ] Retrieval precision/recall (or an honest qualitative equivalent) is reported.
- [ ] Answer groundedness / citation accuracy is reported, not assumed.
- [ ] Structured logging/tracing exists across the agent pipeline (at minimum, correlation-ID based step logging).

## H. Automated Tests

- [ ] Automated tests exist for ingestion, retrieval, and the agent pipeline.
- [ ] The test suite passes, and the pass/fail output is captured in `BACKEND_VERIFICATION.md` §7.

## I. Frontend (only applicable once Gate 1 was approved)

- [ ] React + Vite chat/query interface is wired to `/query` and `/research`.
- [ ] A report viewer renders generated reports.
- [ ] Dashboard for trend/aggregate views is present **or** explicitly deferred to backlog with user sign-off (per the Gate 0 default in `PROMPT.md` §2.2).
- [ ] A manual end-to-end test is recorded: a question asked in the UI produces a cited answer rendered correctly.

## J. Deployment & Deliverables (`PRD.md` §7)

- [ ] Backend (and frontend, if built) is Dockerized.
- [ ] Live deployment exists **or** local-run instructions are clearly documented as the agreed alternative (per Gate 0).
- [ ] `README.md` has complete, accurate, current setup/run instructions.
- [ ] Technical report is written, covering design decisions, architecture choices, trade-offs, challenges faced, and future improvements.
- [ ] Demo video (10–20 minutes) exists, walking through architecture and live usage.
- [ ] GitHub repository is in a clean, submittable state.

## K. Documentation Completeness

- [ ] `PRD.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md`, `BACKEND_VERIFICATION.md`, `PROMPT.md` are all present, current, and internally consistent (no contradictions between what `DECISIONS.md` says and what was actually built).
- [ ] `BACKEND_VERIFICATION.md` has no unfilled `...` template placeholders remaining.
- [ ] `ROADMAP.md` status markers (`[ ]`/`[~]`/`[x]`) accurately reflect what's actually been verified, not aspirational status.

## L. Demo Readiness — Business Question Bank Coverage (`PRD.md` §5)

For each category, at least one representative question has been run through the live system with a correct-looking, cited answer captured as evidence:

- [ ] Customer Intelligence (e.g., most common complaints in the last six months)
- [ ] Product Intelligence (e.g., most frequently requested features across sources)
- [ ] Engineering Intelligence (e.g., which reported issues were eventually fixed)
- [ ] Executive Intelligence (e.g., executive summary of risks/opportunities/recommendations)
- [ ] Research Intelligence (e.g., comprehensive trend/pain-point/recommendation report)

---

## Final Sign-Off

- **Criteria met:** ____ / (total checkbox count above)
- **Unmet criteria and reasons:** ___________________________
- **User review:** [ ] Reviewed  [ ] Approved as complete  [ ] Approved as complete-with-known-gaps (gaps listed above)

The agent may only tell the user "the project is complete" once every box above is checked with cited evidence. A partial result is reported as partial, with the exact gap list — never rounded up.
