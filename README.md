# AI Learning & Job Assistant

Personal portfolio and learning lab by **Ziv Grinblat** — Security Engineer at eToro, building toward **agentic engineering**, **research tooling**, and **biology-adjacent** software.

One FastAPI backend powers three live surfaces:

| Page | URL (local) | What it does |
|------|-------------|--------------|
| **Portfolio** | `/` | About, skills, experience, links to projects |
| **Book Notes** | `/notes.html` | Reading notes by book, AI connections, export |
| **DNA Lab** | `/dna.html` | GC content, reverse complement, nucleotide counts |

**Live:** [ai-learning-job-assistant.onrender.com](https://ai-learning-job-assistant.onrender.com)

---

## Stack

- **Backend:** Python 3.12, FastAPI, SQLite, Pydantic, OpenAI (related-notes agent)
- **Frontend:** HTML, CSS, vanilla JavaScript (no framework)
- **Deploy:** Docker, Render (persistent disk for SQLite)
- **Tests:** pytest (109 tests)

---

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional — for real AI connections (not needed for tests)
# Create .env in project root: OPENAI_API_KEY=sk-...

uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — the API serves the frontend and docs.

Run tests:

```bash
pytest
```

---

## Features

### Portfolio (`/`)
- Profile driven by `frontend/data/profile.json` (skills, experience, target roles, GitHub highlights)
- LinkedIn, GitHub, WhatsApp, optional resume PDF and email

### Book Notes (`/notes.html`)
- Book-first UI: sorted library sidebar → workspace per book
- Short notes (150 chars), chapter tracking, edit / delete / reorder
- Full-text search within a book (`GET /notes?q=`)
- Export book as Markdown
- **AI Connections** — OpenAI picks up to 3 related notes with reasons (stub fallback if no API key)

### DNA Lab (`/dna.html`)
- Paste raw DNA or FASTA; named example sequences
- GC content, reverse complement, nucleotide counts + chart
- Same API as Book Notes

---

## Project layout

```
app/
  main.py                 # FastAPI app, dotenv, static frontend
  api/routes.py           # HTTP endpoints
  schemas/                # Pydantic models (notes, bio, agent, …)
  services/
    note_store.py         # SQLite — notes, books, search, stats
    note_agent.py         # LLM related-notes (OpenAI)
    bioinformatics.py     # DNA analysis
    booksearch.py         # Open Library similar-books
    text_analyzer.py      # Text analysis helpers

frontend/
  index.html              # Portfolio home
  notes.html              # Book Notes app
  dna.html                # DNA Lab
  data/profile.json       # Portfolio content (edit this)
  js/                     # app.js, home.js, dna.js, site.js
  css/                    # styles.css, portfolio.css, dna.css
  assets/                 # resume.pdf (optional)

tests/                    # pytest — API + services
data/notes.db             # SQLite (gitignored; persisted on Render disk)
```

---

## API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Server status |
| GET | `/notes` | List notes (`?book=`, `?sort=`, `?q=` search) |
| POST | `/notes` | Save a note |
| PATCH | `/notes/{id}` | Update a note |
| DELETE | `/notes/{id}` | Delete a note |
| PUT | `/notes/reorder` | Custom sort order |
| POST | `/notes/{id}/related` | AI related notes (max 3) |
| GET | `/notes/count` | Total note count |
| GET | `/books` | Library (book + note count) |
| GET | `/books/stats?book=` | Notes, chapters, last updated |
| GET | `/books/similar?book=` | Similar titles (Open Library) |
| POST | `/bio/gc-content` | DNA GC % |
| POST | `/bio/reverse-complement` | Reverse complement |
| POST | `/bio/nucleotide-counts` | A/T/G/C counts |
| POST | `/analyze-text` | Text stats |
| POST | `/clean-text` | Normalize text |

Interactive docs: `/docs`

---

## Environment variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `OPENAI_API_KEY` | `.env` locally, Render dashboard | Powers related-notes AI |

Without the key, related notes fall back to a stub so the app and tests still work.

---

## Deploy (Render)

- `Dockerfile` + `render.yaml` Blueprint
- Persistent disk mounted at `/app/data` so SQLite survives redeploys
- Set `OPENAI_API_KEY` in Render environment variables

---

## How features are built

```
Service → Schema → Test → Route → Frontend
```

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for what each layer does, build order, and what breaks if you skip a step.

---

## Docs for development

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — layers, functions, request lifecycle, feature checklist
- **[GUIDE.md](GUIDE.md)** — patterns, traps, cheat sheets
- **[LEARNING_DIARY.md](LEARNING_DIARY.md)** — mistakes and fixes log

---

## About

Built as a hands-on path from security engineering into backend and fullstack development — real APIs, real tests, real deployment. Portfolio content lives in `frontend/data/profile.json`; update skills and experience there without touching layout code.

**Looking for:** Agentic Engineer · Researcher · Biology & Healthcare roles.

[LinkedIn](https://www.linkedin.com/in/ziv-grinblat-69429a257/) · [GitHub](https://github.com/ZivGrinblat)
