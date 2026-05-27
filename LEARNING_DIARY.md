# Learning diary — mistakes & fixes

A running log of real bugs and confusions. Not shame — patterns to recognize faster next time.

---

## 2026-05-27

### JavaScript

| # | Mistake | Why it’s wrong | Fix / rule |
|---|---------|----------------|------------|
| 1 | Thought `const` stops the user from changing data | Users change the DOM, not your variables. `const` only locks the **variable name**, not the object’s fields. | `const btn = ...; btn.disabled = true` is fine. `btn = other` is not. |
| 2 | Wrote `` `${len}/150` `` as division in a rewrite | Text outside `${}` is literal. Only **inside** `${}` is JavaScript. | `` `${len}/150` `` → display `42/150`. Division would be `` `${len / 150}` ``. |
| 3 | Thought `checkHealth()` must finish before `loadNotes()` | Without `await`, both start immediately (fire-and-forget). | Order only matters if you **await** each call. |
| 4 | Thought `res.json()` waits on `res.ok` | Second `await` needs the **response object** from the first `await`, not the status check. | `fetch` → `res` → `res.json()`. |
| 5 | `# FILTER FLOW` comments in `<script>` | `#` is Python. In JS use `//`. | Broke the whole script block. |

**Example (async chain):**
```javascript
const res = await fetch(url);      // 1 — get response
const data = await res.json();     // 2 — needs res from step 1
```

**Example (callbacks — no parentheses):**
```javascript
addEventListener("input", loadNotes);   // ✓ pass function
addEventListener("input", loadNotes()); // ✗ calls now, passes undefined
```

---

### Frontend / UX logic

| # | Mistake | Why it’s wrong | Fix / rule |
|---|---------|----------------|------------|
| 6 | Built filter URL in `loadNotes` but no listener on `#bookFilter` | Code existed; nothing triggered it on typing. | `bookFilter.addEventListener("input", loadNotes)`. |
| 7 | `loadNoteCount()` and `loadNotes()` both set `#noteCount` | Two functions, one badge — last write wins. | Decide: **total in DB** (count endpoint) vs **shown after filter** (`notes.length`). Don’t mix. |

---

### Python service (`note_store.py`)

| # | Mistake | Why it’s wrong | Fix / rule |
|---|---------|----------------|------------|
| 8 | `get_note(id, return_all=True)` for “filter by book” | Wrong feature — that’s get-by-id, not filter-by-book. | One function, one job. Filter → `WHERE book = ?`. |
| 9 | `row = ...fetchall()` then `for row in rows` | Variable name typo → `NameError`. | `fetchall()` → plural name: `rows`. |
| 10 | `execute(...)` then `return number_of_rows[0]` without `fetchone()` | `execute` returns a **cursor**, not a number. | `.fetchone()` → tuple → `[0]`. |
| 11 | `book['book']` on SQLite rows | Default rows are **tuples**, not dicts. | `row[0]`, `row[1]` or use `row_factory`. |
| 12 | Broken indent / `for row in rows:''` | Syntax error — file won’t import. | Run `python -m py_compile app/services/note_store.py`. |

**Example (COUNT):**
```python
row = connection.execute("SELECT COUNT(*) FROM notes").fetchone()
return row[0]  # e.g. 5
```

**Example (GROUP BY books):**
```python
# row = ("The Muslim Jesus", 3)
{"book": row[0], "note_count": row[1]}
```

---

### FastAPI routes

| # | Mistake | Why it’s wrong | Fix / rule |
|---|---------|----------------|------------|
| 13 | Three `@router.get("/notes")` handlers | FastAPI keeps one; rest ignored. | One route, optional query: `book: str \| None = None`. |
| 14 | Route function named `get_books` while importing `get_books` | Name **shadows** import → calls itself → recursion. | Route: `get_books_endpoint`. Service: `get_books`. |

**Example:**
```python
from app.services.note_store import get_books

@router.get("/books", response_model=list[BookSummary])
def get_books_endpoint():
    return get_books()
```

---

### Tests

| # | Mistake | Why it’s wrong | Fix / rule |
|---|---------|----------------|------------|
| 15 | `assert count == 5` with empty DB | Arrange didn’t create data. | Save notes **before** assert. |
| 16 | Test named “wrong_number” asserting `count == 2` with 1 note | Tests must pass when code is correct. | Test real cases: empty → 0, two saves → 2. |
| 17 | Copied `LOG_FILE_PATH` monkeypatch for notes API test | Wrong layer — notes need `DB_PATH`. | `monkeypatch.setattr("app.services.note_store.DB_PATH", ...)`. |
| 18 | POST body used `"note"` instead of `"note_text"` | Schema rejects → 422 → nothing saved → count stays 0. | Match **schema field names** exactly. |
| 19 | Test name “two” but three POSTs and `assert count == 3` | Name and assert should match. | Rename or change POSTs. |
| 20 | Filter test without `assert len(data) == 1` | Only checked first row, not that filter excluded others. | Assert **length** + content. |

**Example (API test skeleton):**
```python
def test_something(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))
    init_db()
    # arrange → act → assert
```

---

### try/except (API vs network)

| When | Meaning |
|------|---------|
| `else` on `if res.ok` | Server answered, but status not 2xx (e.g. 404). |
| `catch` on `fetch` | Request never reached server (down, CORS, network). |

---

### Meta — how to study (not a “bug”, a pattern)

| Pattern | What helps |
|---------|------------|
| Reading 600 lines passively | One function → close file → write input/output in 3 lines. |
| Jumping UI + route + SQL same hour | Build **bottom up**: service → route → test → frontend. |
| “I don’t know anything” after integration | You’re learning **wiring**; that’s harder than syntax. Use the 5 boxes: User → JS → Route → Service → SQL → back. |

---

## Quick checklist (before saying “done”)

- [ ] Service returns consistent dict shape?
- [ ] Route name ≠ imported service function name?
- [ ] Schema field names match JSON in tests (`note_text`)?
- [ ] `fetchone()` / `fetchall()` used correctly?
- [ ] Test arrange creates the data you assert?
- [ ] Frontend: listener + fetch URL + render all wired?

---

*Add a new `## YYYY-MM-DD` section after each serious coding day.*
