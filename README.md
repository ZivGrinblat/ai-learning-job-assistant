# Book Notes — AI Learning & Job Assistant

FastAPI backend + SQLite + a single-page frontend for saving reading notes, browsing your library, and finding similar books via Open Library.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open `frontend/index.html` in your browser (with the API running on `http://127.0.0.1:8000`).

Run tests:

```bash
pytest
```

## Project layout

```
app/
  main.py                 # FastAPI app, CORS
  cli.py                  # CLI (argparse)
  api/routes.py           # HTTP endpoints
  schemas/                # Pydantic request/response models
  services/
    note_store.py         # SQLite — notes & books
    booksearch.py         # Open Library similar-books lookup
    text_analyzer.py      # Text analysis helpers
    audit_logger.py       # API request logging

frontend/
  index.html              # App shell (HTML only)
  css/styles.css          # Styles
  js/app.js               # Fetch, render, event handlers
  mockups/                # UI mockups (not wired to API)

learn/js-from-scratch/    # Small JS exercises (standalone HTML)

tests/                    # pytest — services + API

data/notes.db             # SQLite DB (gitignored, created on first save)
logs/                     # Audit logs (gitignored)
```

## API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Server status |
| POST | `/analyze-text` | Text stats |
| POST | `/clean-text` | Normalize text |
| GET | `/notes` | List notes (`?book=` optional filter) |
| POST | `/notes` | Save a note |
| DELETE | `/notes/{id}` | Delete a note |
| GET | `/notes/count` | Total note count |
| GET | `/books` | Library summary (book + note count) |
| GET | `/books/similar?book=` | Similar titles (Open Library) |

Interactive docs: `http://127.0.0.1:8000/docs`

## Docs for you

- **[GUIDE.md](GUIDE.md)** — patterns, traps, cheat sheets (read when stuck)
- **[LEARNING_DIARY.md](LEARNING_DIARY.md)** — your mistakes and fixes log

## How features are built

```
Service → Schema → Route → Test → Frontend
```

Services hold logic. Routes connect HTTP. Schemas define shapes. Tests prove behavior. Frontend calls the API.
