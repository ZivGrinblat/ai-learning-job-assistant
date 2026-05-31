# Architecture — how this app is built

Read this when you want to understand **what each layer does**, **why the order matters**, and **what breaks if you skip a step**.

---

## The five layers (outside → in)

```
Browser (HTML/JS)  →  Route  →  Service  →  Database / OpenAI / HTTP
                         ↑
                      Schema  (defines shapes at the HTTP boundary)
                         ↑
                      Test    (proves each layer before you wire the next)
```

| Layer | Folder / file | Job | Knows about HTTP? | Knows about SQLite? |
|-------|---------------|-----|-------------------|---------------------|
| **Schema** | `app/schemas/` | Valid shapes for JSON in/out | Only as Pydantic models | No |
| **Service** | `app/services/` | Business logic, I/O | No | Yes (if DB) |
| **Route** | `app/api/routes.py` | Map URL + method → service call | Yes | No (calls service) |
| **Test** | `tests/` | Assert behavior | Uses TestClient | Uses temp DB via monkeypatch |
| **Frontend** | `frontend/js/` | User clicks → fetch → DOM | Yes (fetch URLs) | No |

**Rule:** dependencies point **inward**. Routes import services. Services do **not** import routes. Schemas are imported by routes (and sometimes services when building typed responses).

---

## Build order — and what happens if you get it wrong

This is the order you should add a **new feature** (example: book stats).

### 1. Service first (logic + data)

Write a function that does the work with plain Python types (`dict`, `int`, `list`).

```python
def get_book_stats(book_name: str) -> dict | None:
    ...
```

| If you skip it | If you do it too late |
|----------------|----------------------|
| Route has nowhere to call; you put SQL in the route (messy, untestable) | You already wrote tests/routes against fake logic; rework |

| If you do it before schema | That's fine — services don't need schemas |

### 2. Schema (contract)

Define what crosses the HTTP boundary: request body fields, response fields, validation rules.

```python
class BookStats(BaseModel):
    book: str
    note_count: int
    ...
```

| If you skip it | If you do it before service |
|----------------|------------------------------|
| FastAPI still works but no auto-validation/docs; easy to return wrong JSON | Harmless — schema describes intent; service fills it later |

| If you do it after route | Route can't declare `response_model=BookStats`; `/docs` is wrong |

### 3. Test (prove service, then route)

- **Service test** (`tests/test_notes.py`): call `get_book_stats("Dune")` directly — fast, no HTTP.
- **Route test** (`tests/test_api.py`): `client.get("/books/stats?book=Dune")` — proves wiring + status codes (404, 422).

| If you skip it | If you test only the route |
|----------------|---------------------------|
| Regressions when you refactor; you won't trust deploy | Harder to see *where* it broke (HTTP vs SQL) |

| If you test before service exists | Test fails until service exists — that's the point (red → green) |

### 4. Route (thin adapter)

```python
@router.get("/books/stats", response_model=BookStats)
def get_book_stats_endpoint(book: str):
    stats = get_book_stats(book)
    if stats is None:
        raise HTTPException(404, ...)
    return stats
```

Route jobs only:
- Parse query/path/body (FastAPI + schema)
- Call **one** service function (or a short chain)
- Map errors to HTTP status (`404`, `422`)
- Return dict or Pydantic model

| If you skip it | If route comes before service |
|----------------|------------------------------|
| No HTTP access; frontend can't call it | Route is hollow or contains SQL — anti-pattern |

| If you put logic in the route | Works once; untestable without HTTP; duplicate logic later |

### 5. Frontend (optional for API-only features)

`fetch(`${API_BASE}/books/stats?book=...`)` → update DOM.

| If you skip it | If frontend comes before route |
|----------------|--------------------------------|
| API still testable via pytest/curl | 404 in browser; wasted UI work |

---

## Request lifecycle (one example)

**User clicks "Connect" on a note → related notes appear**

```
1. app.js          POST /notes/5/related
2. routes.py       related_notes_endpoint(5)
3. note_agent.py   find_related_notes(5)
4. note_store.py   get_note_by_id(5), get_notes()
5. note_agent.py   OpenAI or stub → RelatedNotesResponse
6. routes.py       return JSON (or 404)
7. app.js          render cards in AI Connections zone
```

Schemas involved: `RelatedNotesResponse`, `RelatedNoteItem` — FastAPI serializes them to JSON automatically.

---

## `app/main.py` — application entry

| Piece | Role |
|-------|------|
| `load_dotenv()` | Loads `.env` (e.g. `OPENAI_API_KEY`) before services read `os.getenv` |
| `FastAPI(...)` | Creates the app object |
| `CORSMiddleware` | Allows browser from other origins to call API (dev convenience) |
| `include_router(router)` | Attaches all endpoints from `routes.py` |
| `on_startup → init_db()` | Creates SQLite file/table before first request |
| `StaticFiles` mount `/` | Serves `frontend/` — **must be last** or it catches `/health`, `/notes`, etc. |

---

## `app/api/routes.py` — HTTP surface

Grouped by domain. Each handler should be **thin**.

| Endpoint group | Service(s) | Schema(s) |
|----------------|------------|-----------|
| `/health` | none | none |
| `/analyze-text`, `/clean-text` | `text_analyzer`, `audit_logger` | `text_analysis` |
| `/notes/*` | `note_store` | `notes` |
| `/books/*` | `note_store`, `booksearch` | `notes` |
| `/bio/*` | `bioinformatics` | `bio` |
| `/notes/{id}/related` | `note_agent` | `agent` |

**Important pattern:** `ValueError` from bio services → `HTTPException(422)`. Missing note → `404`. Invalid `sort` query → `422`.

---

## `app/schemas/` — contracts, not logic

Pydantic models validate **at the edge** (when FastAPI parses a request or builds a response).

### `schemas/notes.py`

| Model | Direction | Purpose |
|-------|-----------|---------|
| `NoteRequest` | In (POST) | book/chapter/text limits enforced before save |
| `NoteUpdateRequest` | In (PATCH) | same fields for edits |
| `ReorderNotesRequest` | In (PUT) | ordered list of ids |
| `NoteResponse` | Out | `{message, id}` after create/update |
| `NoteItem` | Out | one row for list endpoints |
| `BookSummary` | Out | library sidebar: book + count |
| `BookStats` | Out | aggregated stats for one book |
| `SimilarBook` | Out | Open Library hit |

**Why separate Request vs Item:** request has no `id`/`created_at` (client doesn't send them). Item is what the DB returns.

### `schemas/agent.py`

| Model | Purpose |
|-------|---------|
| `RelatedNoteItem` | One related note + human-readable `reason` from LLM |
| `RelatedNotesResponse` | Source id + up to 3 related (enforced by `max_length=3`) |

### `schemas/bio.py`

| Model | Purpose |
|-------|---------|
| `DnaRequest` | Input sequence (max 1000 — matches frontend counter) |
| `DnaResponse`, `ComplementDnaResponse`, `NeucleotidsCounts` | Typed outputs for each bio endpoint |

### `schemas/text_analysis.py`

Early learning endpoints — word/char/line counts and cleaned text.

---

## `app/services/note_store.py` — SQLite persistence

**Single source of truth for notes data.** Routes never write SQL here.

| Function | What it does | Returns |
|----------|--------------|---------|
| `init_db()` | Create `data/notes.db`, table, migrate `sort_order` if missing | nothing |
| `_ensure_schema()` | ALTER TABLE for older DBs without `sort_order` | nothing |
| `_row_to_note()` | Tuple row → dict keys frontend expects | dict |
| `save_note()` | INSERT with next `sort_order` | new id |
| `update_note()` | UPDATE by id | bool (found?) |
| `delete_note()` | DELETE by id | bool |
| `reorder_notes()` | Set `sort_order` from id list position | nothing |
| `get_notes()` | Filter by book, search `q`, sort mode | list[dict] |
| `get_note_by_id()` | Single note for agent/edit | dict or None |
| `get_book_stats()` | Derives counts from notes (no extra SQL) | dict or None |
| `get_books()` | GROUP BY book for library | list[dict] |
| `count_notes()` | Total rows | int |
| `count_notes_for_one_book()` | COUNT for one book | int |

**`DB_PATH`:** constant at module top so tests can `monkeypatch` to a temp file.

**`SORT_CLAUSES`:** maps UI sort names to SQL — keeps SQL out of routes.

---

## `app/services/note_agent.py` — LLM related-notes

| Function | Role |
|----------|------|
| `_stub_related()` | Fallback when no API key or OpenAI fails — first 3 notes, fake reason |
| `_pick_related_with_openai()` | Sends source + candidates as JSON; parses LLM response; validates ids exist |
| `find_related_notes()` | Orchestrator: load source, load others, pick stub vs OpenAI, return `RelatedNotesResponse` |

**Design choice:** service returns `None` if source missing; **route** turns that into 404. Agent doesn't know HTTP.

---

## `app/services/bioinformatics.py` — pure DNA logic

| Function | Role |
|----------|------|
| `validate_dna_string()` | Raises `ValueError` on empty or invalid letters — routes catch this |
| `calculate_gc_content()` | Count G/C, percent |
| `return_reverse_complement_dna_string()` | Complement each base, reverse string |
| `return_neucleotids_counts()` | Per-letter counts |

No I/O — easiest to test in isolation (`tests/test_api.py` and direct unit tests).

---

## `app/services/booksearch.py` — external API

| Function | Role |
|----------|------|
| `find_similar_books()` | GET Open Library search; map to `{title, author}` list |

Network errors bubble up — no try/except here yet (would belong in route or here with a clear policy).

---

## `app/services/text_analyzer.py` — text stats

| Function | Role |
|----------|------|
| `is_empty_or_whitespace()` | Guard for all counters |
| `count_words/lines/characters()` | Small pure helpers |
| `clean_text()` | Collapse whitespace |
| `analyze_text()` | Bundle for `/analyze-text` response dict |

---

## `app/services/audit_logger.py` — side-effect logging

| Function | Role |
|----------|------|
| `write_api_log()` | Append JSON entry to `logs/api_requests.log` — used by text endpoints only |

Not on notes/bio paths — intentional scope from early learning.

---

## Frontend JavaScript map

### `frontend/js/site.js`

Shared on notes + DNA pages.

| Piece | Role |
|-------|------|
| `Site.apiBase` | Same origin in prod; localhost when opening HTML as file |
| `Site.checkHealth()` | Polls `/health`, updates status dot |
| `Site.injectFooter()` | Adds nav footer on non-portfolio pages |

### `frontend/js/home.js`

Portfolio only — loads `data/profile.json`, renders sections (no backend except health via site if present).

| Function | Role |
|----------|------|
| `renderProfile()` | JSON → DOM (experience, skills, projects) |
| `loadProfile()` | fetch profile.json |
| `escapeHtml()` | Prevent XSS when inserting user-ish strings |

### `frontend/js/app.js`

Book Notes — largest file.

| Function | Role |
|----------|------|
| `getBookFilter()` | Which book query param to send (respects new-book mode) |
| `loadNotes()` | GET `/notes` with book/sort/q — drives main list |
| `saveNote()` | POST or PATCH depending on `editingNoteId` |
| `selectBook()` | Sets `activeBook`, reloads notes + stats + similar books |
| `loadSimilarBooks()` | GET `/books/similar` |
| `connectRelatedNotes()` | POST `/notes/{id}/related` → AI Connections UI |
| `exportBookNotes()` | Client-side Markdown download from `loadedNotes` |
| Drag/reorder handlers | PUT `/notes/reorder` after DOM reorder |

State variables at top (`activeBook`, `loadedNotes`, …) are the **frontend's memory** — mirror of what the backend stores.

### `frontend/js/dna.js`

| Function | Role |
|----------|------|
| `parseFasta()` | Strip headers/whitespace before API call |
| `analyzeDna()` | Parallel POSTs to three `/bio/*` endpoints |
| `renderNucleotideChart()` | Pure DOM from counts response |

---

## Tests — what each file guards

| File | Tests |
|------|-------|
| `test_notes.py` | `note_store` service directly |
| `test_text_analyzer.py` | text functions |
| `test_audit_logger.py` | log file writes |
| `test_api.py` | Full HTTP stack via `TestClient` |
| `test_cli.py` | CLI entry |

**Pattern in `test_api.py`:** `init_db()` in fixtures; monkeypatch `DB_PATH` and `OPENAI_API_KEY` so tests don't touch real disk or OpenAI.

---

## Adding a feature — checklist

1. Name the **service function** and its inputs/outputs (paper).
2. Write **service test** (red).
3. Implement **service** (green).
4. Add **schema** if HTTP shape is new.
5. Add **route** + **route test**.
6. Wire **frontend** if user-facing.
7. Run `pytest`; hit `/docs`; click in browser.

---

## Files you edit most often

| Goal | Start here |
|------|------------|
| New API behavior | `app/services/` |
| Request validation / OpenAPI | `app/schemas/` |
| URL or status code | `app/api/routes.py` |
| Prove it works | `tests/` |
| UI | `frontend/js/` + `frontend/data/profile.json` |

See also **[GUIDE.md](GUIDE.md)** for traps and **[LEARNING_DIARY.md](LEARNING_DIARY.md)** for mistakes you've already made.
