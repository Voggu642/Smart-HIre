# SmartHire — MVP (Minimum Viable Product)

A lean, demo-ready, AI-powered job portal MVP featuring:
- **Job recommendations** (content-based) with explainability
- **Resume analyzer** with actionable suggestions
- **Simple skill graph expansion** (synonyms → canonical skills)
- **Web UI** (vanilla HTML + JS + Tailwind CDN)
- **FastAPI backend**

> This is a lightweight prototype intended for seminars/demos and easy extension.

---

## Quick Start

### 1) Python backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```
The API runs at: **http://127.0.0.1:8000**  
Docs at: **http://127.0.0.1:8000/docs**

### 2) Frontend
Open `frontend/index.html` directly in your browser, or serve it with a local server:
```bash
# Option A: Python simple server (from the project root or frontend/)
python -m http.server 5500
# then visit http://127.0.0.1:5500/frontend/
```

> Ensure the backend is running on port 8000. If you change ports, update the `API_BASE` in `frontend/app.js`.

---

## Project Structure

```
SmartHire-MVP/
├── backend/
│   ├── app.py
│   ├── recommender.py
│   ├── resume_analyzer.py
│   ├── models.py
│   ├── requirements.txt
│   └── sample_data/
│       ├── jobs.json
│       └── skills_graph.json
├── frontend/
│   ├── index.html
│   └── app.js
└── README.md
```

---

## Notes & Next Steps
- Replace TF‑IDF with transformer embeddings (e.g., `sentence-transformers`) when ready.
- Add authentication, recruiter dashboard, and RL-based feedback loops post-MVP.
- Expand `skills_graph.json` with your domain skills & synonyms.
- Add persistence (DB) and real resume parsing (PDF/DOCX).
