# PROMPT.md
### Master Spec-Driven Execution Prompt — Autonomous Product Intelligence & Decision Support System

> **This file is the execution contract for the build.** It does not replace `AGENT.md`, `PRD.md`, `ARCHITECTURE.md`, `DECISIONS.md`, or `ROADMAP.md` — it sequences them and adapts them to an accelerated 1-day implementation timeline while preserving all engineering gates and evidence requirements. `AGENT.md` is read and obeyed **first, in full, before anything else**. `OUTCOME.md` is read **last** — nothing is declared "done" until every line in it is checked off with evidence.

---

## 0. Mandatory Read Order

1. **`AGENT.md`** — operating rules, hard gates, non-negotiables. Read in full before any planning, scaffolding, or code. Nothing in this file or in chat overrides it; any conflict must be flagged to the user before proceeding.
2. **`PRD.md`** — what is being built, target users, acceptance test bank (§5), deliverables, evaluation criteria.
3. **`ARCHITECTURE.md`** — layered system design, component responsibilities, API contract, tech stack proposal.
4. **`DECISIONS.md`** — the running log of confirmed decisions. Section 2 below tells you exactly what to write into it before Phase 1.
5. **`ROADMAP.md`** — the original phase breakdown. Section 3 below is the same phases, timeboxed for a 5–7 day demo.
6. **This file (`PROMPT.md`)** — the phase-by-phase execution contract, read in order, one phase active at a time.
7. **`OUTCOME.md`** — the final certification checklist. Read only when every phase in Section 3 reports complete. The project is not finished until every line in `OUTCOME.md` passes with evidence in the repo.

If any of these files is missing, stop and ask — do not reconstruct it from memory.

---

## 1. Operating Contract (inherits `AGENT.md`, does not relax it)

- All nine non-negotiable principles in `AGENT.md` §2 remain fully in force for this build, including on a compressed timeline. A short timeline is a reason to scope tightly (§8 "Explicit Freedoms" / "Out of Scope" in `PRD.md`), never a reason to skip a gate, skip evidence, or silently assume.
- **Backend-first hard gate stays in force.** Zero frontend code, zero frontend scaffolding, zero frontend dependency installs until Gate 1 (`BACKEND_VERIFICATION.md`) is produced and the user explicitly approves moving to Phase 4.
- **Evidence-over-claims stays in force.** No task, phase, or `ROADMAP.md` checkbox is marked done without a runnable demonstration (test output, curl/Postman call with real response, log excerpt).
- **Mocked/synthetic data is pre-approved for this build** (see §2 — "Locked Decisions"), because the user has explicitly authorized synthetic data as the demo dataset. It must still be clearly labeled `MOCK`/`SYNTHETIC` in code, fixtures, logs, and the README, per `AGENT.md` §2.9.
- **No new silent defaults.** Any ambiguity discovered mid-build that is not already resolved in §2 below must be logged as an open question in `CLARIFICATION_QUESTIONS.md` and asked about in chat — not defaulted and built around.
- **Traceability stays in force.** Every decision in §2, and any new decision made mid-build, is logged in `DECISIONS.md` at the time it is made, with context / options considered / decision / rationale / trade-offs / source.

---

## 2. Gate 0 — Locked Decisions vs. Still-Open Items

The user has already made a set of real decisions outside the formal Gate-0 Q&A. Per `AGENT.md` §4, these must be transcribed into `DECISIONS.md` (as "user-specified," dated) **before Phase 1 starts** — but the remaining Gate-0 questions that were *not* actually answered must still be asked, not defaulted. Do not treat "we have some decisions" as "Gate 0 is fully cleared."

### 2.1 Locked (write to `DECISIONS.md` verbatim, source = user-specified)

| # | `CLARIFICATION_QUESTIONS.md` ref | Locked decision |
|---|---|---|
| 1 | A.1 Data sources | Synthetic/sample data: generate realistic support tickets, GitHub issues, PRDs, meeting notes, and release notes across a small number of fictional product areas. |
| 4 | B.4 LLM provider | Claude via the Anthropic API, used for all reasoning/generation/agent steps. |
| 7 | C.7 Orchestration | Custom lightweight orchestrator (not LangGraph/CrewAI), documented explicitly. |
| 8 | C.8 Vector DB | Chroma. |
| — | (structured store, not in original question bank but decided) | SQLite for structured/metadata fields (ticket status, dates, product area, etc.). |
| 9 | C.9 Backend framework | Python + FastAPI. |
| 13 | E.13 Frontend framework | React + Vite (build order unaffected — still Phase 4 only). |
| 17/18 | G.17/18 Timeline & priority | Hard target: demoable end-to-end within 1 day. Priority is a clean, correct, demonstrable core workflow (ingestion → hybrid RAG → multi-agent reasoning → memory → API) over infra polish or exhaustive breadth. |

### 2.2 Still Open — must be asked before Phase 1 begins (do not default silently)

| # | Ref | Question | Proposed default (needs explicit sign-off) |
|---|---|---|---|
| 2 | A.2 | Scale to design for | ~150–400 synthetic documents total across sources — enough to demonstrate aggregation/trend questions, not a load test. |
| 3 | A.3 | Must-have vs. nice-to-have question categories | All 5 categories in `PRD.md` §5 at "answerable, demo-quality" depth; Research Intelligence's comprehensive-report question is the one allowed to be lighter if time runs short. |
| 5 | B.5 | API budget constraint during dev/demo | None assumed — flag immediately if usage/cost becomes a blocker. |
| 6 | B.6 | Embeddings model/provider | Default to a Chroma-compatible local/open embedding model (e.g., `sentence-transformers`) to avoid a second paid API dependency — **needs confirmation**, since it wasn't part of the locked decisions. |
| 10 | C.10 | Streaming vs. batch ingestion | Batch ingest-then-query for v1. |
| 11 | D.11 | What long-term memory persists | Default: prior Q&A history + discovered findings/insights. User preferences deferred to backlog unless requested. |
| 12 | D.12 | Memory backend | Default: a dedicated namespace/table (not conflated with the document vector store), to keep memory retrieval separate from RAG retrieval. |
| 14 | E.14 | UI requirements | Default: chat/query interface + report viewer as must-have; trend dashboard as stretch, only if Phases 1–3 finish early. |
| 15/16 | F.15/16 | Deployment target | Given the 5–7 day demo priority, default is **local run + demo video**, with live deployment only attempted if time remains — matches `PRD.md` §7 ("live deployment (preferred)," not mandatory). |
| 19/20 | H.19/20 | Repo & tooling conventions | Default: new repo, standard `pytest` + `ruff`/`black` conventions, no CI pipeline required for a demo submission. |

**Exit criteria for Gate 0 in this build:** the table in 2.1 is transcribed into `DECISIONS.md`, and every row in 2.2 has either a user answer or explicit sign-off on the proposed default, recorded in `DECISIONS.md`. Only then does Phase 1 begin.

---

## 3. Phase Plan (Accelerated 1-Day Execution)

The engineering process remains unchanged. Only the execution schedule is compressed.

Every phase still requires:
- Evidence
- Documentation updates
- Roadmap updates
- Explicit checkpoint approval

### Phase 0 — Gate 0 (30 minutes)
- Read AGENT.md, PRD.md, ARCHITECTURE.md, DECISIONS.md, ROADMAP.md and PROMPT.md.
- Record locked decisions into DECISIONS.md.
- Resolve remaining Gate 0 questions.
- Obtain explicit approval before implementation.

### Phase 1 — Backend Foundations (2 hours)
- Repository scaffolding (FastAPI, SQLite, Chroma).
- Synthetic dataset generation.
- Ingestion pipeline.
- `/health` and `/ingest`.
- Evidence: curl output, SQLite verification, Chroma verification.

### Phase 2 — Retrieval & Multi-Agent Layer (3 hours)
- Hybrid Retrieval.
- Planner, Retrieval, Analysis, Validation and Report Writer agents.
- `/query` and `/research`.
- Evidence: representative questions from every PRD category with citations.

### Phase 3 — Memory, Evaluation & Backend Verification (1.5 hours)
- Persistent memory.
- Evaluation harness.
- Structured logging.
- Automated tests.
- Complete BACKEND_VERIFICATION.md.
- Gate 1 approval before frontend.

### Phase 4 — Frontend MVP (1.5 hours)
- React + Vite.
- Chat interface.
- Report viewer.
- Dashboard only if time remains.
- Evidence: successful end-to-end UI demonstration.

### Phase 5 — Finalization (1 hour)
- Dockerize.
- README.
- Technical report.
- Demo preparation.
- Validate every applicable OUTCOME.md checklist item with evidence.

---



## 3.1 One-Day Execution Mode

The 1-day timeline does not relax engineering standards.

The following remain mandatory:
- Backend-first development.
- Gate 0 and Gate 1.
- Evidence-based verification.
- Documentation updates.
- Decision logging.
- API verification.
- Automated testing where applicable.

Only the implementation cadence changes.

## 4. Documentation Discipline (inherits `AGENT.md` §7)

| File | Updated when |
|---|---|
| `PRD.md` | Rarely — only on user-approved scope change |
| `ARCHITECTURE.md` | Whenever a design decision is made |
| `CLARIFICATION_QUESTIONS.md` | During Gate 0, and again if new ambiguity surfaces mid-build |
| `DECISIONS.md` | Continuously, at the moment each decision is made |
| `ROADMAP.md` | After every phase/checkpoint |
| `BACKEND_VERIFICATION.md` | End of Phase 3, before Gate 1 |
| `README.md` | Continuously as features land |
| `PROMPT.md` (this file) | Only if the phase plan itself changes — logged as a decision |
| `OUTCOME.md` | Not updated during the build — only checked against, at the very end |

---

## 5. Final Certification (do this last, not before)

When Phase 5 reports complete, the agent must:
1. Open `OUTCOME.md` and go through every line.
2. For each line, locate the concrete evidence already sitting in the repo (test output, `BACKEND_VERIFICATION.md` entries, README, demo video, logs). Do not write new evidence retroactively to make a line pass — if evidence doesn't exist, the line fails and the gap is disclosed.
3. Report to the user a straight count: "**N of M** `OUTCOME.md` criteria met," listing any unmet lines and why.
4. Only describe the project as "complete" once N = M. A partially met checklist is reported as partial — never rounded up, never described as "essentially done."

If, at any point during the build, the agent realizes it has violated `AGENT.md` (wrote functional code before Gate 0, touched frontend before Gate 1, skipped logging a decision, marked something done without evidence), it stops, discloses the violation, and proposes a remediation before continuing — per `AGENT.md` §9.
