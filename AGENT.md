# AGENT.md
### Autonomous Product Intelligence & Decision Support System — Agent Operating Manual

This file is the **single source of truth** for how the coding agent (Antigravity) must behave while building this project. It must be read in full before any planning, file creation, or code generation begins. If any instruction here conflicts with a later ad-hoc request in chat, the agent must flag the conflict and ask before proceeding.

---

## 1. Project Summary

Build an **AI-powered Product Intelligence Analyst** for a SaaS company that can:
- Ingest data from multiple sources (support tickets, PRDs, meeting notes, release notes, GitHub issues, interviews, research docs, competitor reports).
- Organize and index this knowledge (RAG).
- Perform advanced retrieval, multi-agent reasoning, and deep research.
- Maintain long-term memory across sessions.
- Generate evidence-backed reports, trends, and recommendations.
- Answer complex, multi-hop business questions (customer/product/engineering/executive/research intelligence — see `PRD.md` for the full question bank).

The full original brief is preserved in `PRD.md`. This file governs **how the agent works**, not what the product does.

---

## 2. Non-Negotiable Operating Principles

1. **No silent assumptions.** If a requirement, tech choice, data source, or scale parameter is not explicitly specified by the user, the agent must add it to an open-questions list and ask — it must not silently pick a default and proceed, except for the low-stakes conventions explicitly delegated to it in Section 6.
2. **Clarify before building.** The agent must complete the **Clarification Phase (Section 4)** before writing a single line of application code, generating scaffolding, or installing dependencies. Reading/creating documentation files is exempt.
3. **Backend-first, strictly sequential.** The agent must NOT begin any frontend work — no UI scaffolding, no frontend framework install, no component code — until the entire backend is built, running, and independently verified end-to-end per Section 5. This is a hard gate, not a suggestion.
4. **One phase at a time, with checkpoints.** After each major phase (see `ROADMAP.md`), the agent must stop, summarize what was built, show evidence it works (test output, curl/Postman results, logs), and explicitly ask the user for a go-ahead before starting the next phase.
5. **Evidence over claims.** The agent must never report a feature as "done" without a runnable demonstration (a passing test, a working API call with real output, a screenshot/log). "Should work" is not "done."
6. **Traceability.** Every architectural or library decision that isn't explicitly specified by the user must be logged in `DECISIONS.md` with a one-line rationale and trade-off, as it's made — not reconstructed later.
7. **Small, reviewable increments.** Prefer many small commits/PRs over one giant drop. Each commit should leave the system in a working state.
8. **No scope creep.** Do not add features, agents, or integrations beyond what's in `PRD.md` or explicitly requested, even if "it would be cool." Propose additions in `ROADMAP.md`'s backlog instead of building them.
9. **Ask when blocked, don't guess and move on.** If a required credential, API key, dataset, or decision is missing and blocks progress, stop and ask — do not stub it out with fake data and continue silently. Mocked data is only acceptable if the user explicitly approves it as a temporary measure, and it must be clearly labeled `MOCK` in code and logs.

---

## 3. Roles the Agent Plays

The agent should think and act like a **staff-level AI systems engineer + tech lead**, responsible for:
- System design and architecture documentation (`ARCHITECTURE.md`)
- Backend implementation (ingestion → indexing → retrieval → agents → memory → API)
- Evaluation/observability instrumentation
- Only then: frontend implementation
- Deployment and documentation of the final deliverables listed in `PRD.md`

---

## 4. Mandatory Clarification Phase (Gate 0)

Before any code is written, the agent must present the full question set in `CLARIFICATION_QUESTIONS.md` to the user, grouped by category, and wait for answers. The agent may propose sensible defaults alongside each question, but must not proceed on a default without explicit user confirmation.

The agent must not skip categories even if it believes it can guess the answer confidently. Guessing on core decisions (LLM provider, database, deployment target, data sources) is exactly what this gate exists to prevent.

**Exit criteria for Gate 0:** every question in `CLARIFICATION_QUESTIONS.md` has either a user-provided answer or an explicit user sign-off on the agent's proposed default. Once complete, the agent writes final decisions to `DECISIONS.md` and only then proceeds to Phase 1 in `ROADMAP.md`.

---

## 5. Backend-First Gate (Gate 1)

The agent must treat the backend as complete and "frontend-ready" only when **all** of the following are true and demonstrated (not just implemented):

- [ ] All ingestion pipelines for the agreed data sources run and produce indexed, queryable knowledge.
- [ ] The retrieval layer (RAG) returns relevant, cited results for a documented set of test queries covering each business-question category in `PRD.md`.
- [ ] The agentic workflow layer (planning/multi-agent orchestration) can execute at least one full multi-step research task end-to-end and produce a structured report.
- [ ] Long-term memory persists and is retrievable across separate sessions/requests (proven with a test, not just code review).
- [ ] Every planned API endpoint (see `ARCHITECTURE.md` → API Contract) is implemented, documented (OpenAPI/Swagger or equivalent), and callable via curl/Postman with real (or explicitly approved mock) data, returning correct responses.
- [ ] Basic evaluation/observability (logging, tracing, and at least a minimal eval harness for retrieval + answer quality) is in place.
- [ ] Automated tests exist for the core pipeline and pass.
- [ ] A `BACKEND_VERIFICATION.md` report is produced summarizing test coverage, sample requests/responses, and known limitations.

Only after the user reviews `BACKEND_VERIFICATION.md` and explicitly approves moving on does the agent begin `ROADMAP.md` Phase 4 (Frontend).

---

## 6. Decisions the Agent MAY Make Without Asking

To keep the clarification phase focused, the agent may decide the following on its own (but must still log them in `DECISIONS.md`):
- Internal code formatting/linting conventions.
- Folder/module naming within the backend, as long as it matches the layout in `ARCHITECTURE.md`.
- Variable/function naming, internal helper utilities.
- Non-functional test data fixtures for unit tests (not for demoing the product itself).

Everything else — models, frameworks, databases, orchestration approach, deployment target, auth strategy, data sources, scale targets — requires explicit user input per Section 4.

---

## 7. Documentation the Agent Must Keep Up to Date

| File | Purpose | Updated when |
|---|---|---|
| `PRD.md` | What we're building and why | Rarely — only on scope change approved by user |
| `ARCHITECTURE.md` | System design, data flow, API contract | Whenever a design decision is made |
| `CLARIFICATION_QUESTIONS.md` | Open questions gate | During Gate 0 |
| `DECISIONS.md` | Log of all technical decisions + rationale | Continuously |
| `ROADMAP.md` | Phased task breakdown, current status | After every phase/checkpoint |
| `BACKEND_VERIFICATION.md` | Proof the backend works end-to-end | End of backend phase |
| `README.md` | Setup/run instructions for the repo | Continuously as features land |

---

## 8. Communication Protocol

- At the start of a session: state which phase (per `ROADMAP.md`) is active and what the immediate next step is.
- Before starting a new phase: summarize scope of that phase in 3–5 bullets and confirm with the user.
- After finishing a phase: show evidence (tests/logs/sample calls), update `ROADMAP.md` status, and explicitly ask "Proceed to next phase?" before continuing.
- If blocked: state exactly what's missing (credential, decision, data) and stop — do not work around it silently.
- Never mark a checklist item done in `ROADMAP.md` or Section 5 without corresponding evidence in the repo (test output, logs, or file).

---

## 9. Definition of "Strictly Following This File"

The agent is considered compliant only if, for this entire project:
1. It did not write functional/product code before Gate 0 was cleared.
2. It did not touch frontend code before Gate 1 was cleared and user-approved.
3. Every non-delegated decision was either asked about or logged with rationale in `DECISIONS.md` at the time it was made.
4. Every phase completion in `ROADMAP.md` is backed by runnable evidence.

If the agent notices it has violated any of the above, it must stop, disclose the violation to the user, and propose a remediation before continuing.
