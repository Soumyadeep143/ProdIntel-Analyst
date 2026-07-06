# Product Intelligence Analyst (SaaS Decision Support Platform)

An autonomous AI-powered Product Intelligence Analyst for SaaS companies that ingests support tickets, GitHub issues, product documents (PRDs), meeting logs, and release notes to help teams analyze complaints, track trends, review system health, and generate deep research reports.

The reasoning stack is powered by **Llama 3.3** via **Groq** for sub-second, highly structured agent inferences, combined with a local hybrid semantic vector (ChromaDB + SQLite) search engine.

---

## Repository Structure
* `backend/` - Contains the FastAPI backend application, SQLite/ChromaDB databases, tests, and verification scripts.
* `frontend/` - React + Vite SPA using MongoDB brand teals, Vanilla CSS layout styling, and interactive citation drawers.

---

## 1. Backend Setup & Startup

### Prerequisites
* Python 3.10+
* Groq API Key

### Installation
1. Navigate to the project root:
   ```powershell
   cd C:\Users\dell\ProdIntel_AI
   ```
2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Install backend dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root containing your Groq API Key:
   ```env
   GROQ_API_KEY=gsk_your_api_key_here
   ```

### Start Backend Server
Launch the FastAPI uvicorn development server:
```powershell
.venv\Scripts\uvicorn app.main:app --reload
```
* **Swagger API UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **API Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 2. Frontend Setup & Startup

### Prerequisites
* Node.js (v18+) and npm

### Installation
1. Open a new terminal tab, navigate to the `frontend/` directory, and install packages:
   ```powershell
   cd C:\Users\dell\ProdIntel_AI\frontend
   npm install
   npm install lucide-react
   ```

### Start Frontend Dev Server
Start the React + Vite UI dev server:
```powershell
npm run dev
```
* **UI Interface URL**: [http://localhost:5173/](http://localhost:5173/)

---

## 3. Key User Workflows in the UI

### A. Core Control Panel (Sidebar)
* **Ingest Corpus**: Click "Re-Ingest 1K Docs" to automatically generate 1,000 realistic synthetic tickets and PRD records, storing metadata in SQLite and indexing vectors in ChromaDB.
* **Session Manager**: Toggle between session IDs (e.g. `session_001`, `session_002`) to verify memory persistence. Persistent memories are displayed directly in the panel.
* **Database Health**: Displays live indicators of SQLite and ChromaDB online status.

### B. Q&A Chat Tab
* Input queries (e.g., *"What problems are users reporting about search?"*).
* Returns responses from Llama 3.3 with citation badges (e.g., `support_ticket-001`).
* **Interactive Citations**: Click any citation badge to slide open a **side drawer** showing the full raw text content of that source document.

### C. Deep Research Tab
* Enter research requests (e.g., *"Analyze billing complaints and make a report"*).
* **Multi-Agent Pipeline Tracker**: Displays live stage indicators tracking the 5-stage agent flow (Planner → Retrieval → Analysis → Validation → Report Writer).
* Returns a beautifully structured, citation-backed Markdown report.

### D. System Evaluations Tab
* Click "Run Evals" to execute the offline test harness (`POST /evals/run`).
* Displays aggregated performance scores (**Precision**, **Recall**, and **Groundedness**) with detailed query breakdowns.
