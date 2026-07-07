# Product Intelligence Analyst (SaaS Decision Support Platform)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/react-%23202328.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0080FF?style=for-the-badge)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Llama 3.3](https://img.shields.io/badge/Llama_3.3-orange?style=for-the-badge)
[![Vercel Deployment](https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://prodintel-analyst.vercel.app)
[![Render Deployment](https://img.shields.io/badge/Render-Deployed-%2346E3B7.svg?style=for-the-badge&logo=render&logoColor=white)](https://prodintel-analyst.onrender.com/docs)

An autonomous AI-powered Product Intelligence Analyst for SaaS companies that ingests support tickets, GitHub issues, product documents (PRDs), meeting logs, and release notes to help teams analyze complaints, track trends, review system health, and generate deep research reports.

The reasoning stack is powered by **Llama 3.3** via **Groq** for sub-second, highly structured agent inferences, combined with a local hybrid semantic vector (ChromaDB + SQLite) search engine.

### 🌐 Live Cloud Deployments
* **Live Web Dashboard (Vercel)**: [https://prodintel-analyst.vercel.app](https://prodintel-analyst.vercel.app)
* **Live REST API Docs (Render Swagger)**: [https://prodintel-analyst.onrender.com/docs](https://prodintel-analyst.onrender.com/docs)
* **Live API Health Check (Render)**: [https://prodintel-analyst.onrender.com/health](https://prodintel-analyst.onrender.com/health)

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
