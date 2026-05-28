# Developer Guide — ai-learning-job-assistant

Your personal reference. When you're stuck, check here before asking the AI.

---

## Traps I Keep Falling Into

Read this first when you're stuck. These are patterns you've hit more than once.

### 1. Not everything needs a payload
A `GET` endpoint that returns all items needs **zero parameters**. No payload, no request object. Just call the service and return.
```python
# RIGHT — simple GET
@router.get("/notes")
def get_notes_endpoint():
    return get_all_notes()

# WRONG — overcomplicating it
@router.get("/notes")
def get_notes_endpoint(payload: NoteItem, http_request: Request):
    result = get_all_notes(payload.id, payload.book, ...)  # NO
```

### 2. One insert, not two
When you need to capture the return value of `execute`, don't call it twice. Just add `cursor =` in front of the existing call.
```python
# RIGHT
cursor = connection.execute("INSERT INTO ...", (values,))
new_id = cursor.lastrowid

# WRONG — inserts the data twice
connection.execute("INSERT INTO ...", (values,))
cursor = connection.execute("INSERT INTO ...", (values,))
```

### 3. A function's return value is what it returns, not an object with attributes
If `save_note` returns an integer, then `result` is an integer. Not `result.new_id`, not `result.id`. Just `result`.
```python
# In the service:
return new_id  # returns 5

# In the route:
result = save_note(...)  # result is 5
response = NoteResponse(message="Note saved", id=result)  # not id=result.new_id
```

### 4. Close after you're done, not before
Don't use a connection after closing it. Save any values you need first, then close, then return.

### 5. SQL order matters
It's always `SELECT ... FROM ...`, never `FROM ... SELECT ...`. The action verb comes first.

### 6. Tuples are accessed by position, not by name
`row[0]`, `row[1]` — not `row.book_name`. Unless you set up `row_factory` (we haven't).

---

## Project Structure — Where Things Live

```
app/
  main.py                      # App startup — CORS, router
  cli.py                       # Command-line interface (argparse)
  api/
    routes.py                  # All endpoints — this is where HTTP meets your code
  schemas/
    text_analysis.py           # What the text API accepts and returns
    notes.py                   # What the notes API accepts and returns
  services/
    text_analyzer.py           # Text logic — no HTTP, no schemas, just functions
    audit_logger.py            # Writes API request logs to file
    note_store.py              # Talks to the SQLite database
    booksearch.py              # Open Library — similar books lookup
tests/
  test_text_analyzer.py        # Tests for text analysis functions
  test_cli.py                  # Tests for CLI
  test_api.py                  # Tests for API endpoints
  test_audit_logger.py         # Tests for audit logging
  test_notes.py                # Tests for note_store service
frontend/
  index.html                   # App shell (HTML)
  css/styles.css               # Styles
  js/app.js                    # JavaScript — fetch, render, events
  mockups/                     # UI mockups (preview only)
learn/
  js-from-scratch/             # Standalone JS exercises
data/
  notes.db                     # SQLite database (gitignored — not in repo)
logs/
  api_requests.log             # Audit log (gitignored)
README.md                      # Start here — quick start + layout
LEARNING_DIARY.md              # Your mistakes log
```

**Key rule:** Services don't know about HTTP. Schemas don't know about the database. Routes connect them. This separation is what makes the code testable and changeable.

---

## The Pattern — How Every Feature Gets Built

Every feature in this project follows the same pipeline. Memorize it:

```
1. Service    → Write the logic (pure Python, no HTTP)
2. Schema     → Define what the API accepts and returns (Pydantic)
3. Route      → Connect HTTP to the service
4. Test       → Prove it works
```

### Why this order?

- You can test the service without running the server.
- You can change the database without touching the API.
- You can change the API response shape without touching the logic.

If you're unsure where code belongs, ask: "Is this about HTTP? Then routes. Is this about data shape? Then schemas. Is this about doing work? Then services."

---

## How to Write a Service

File: `app/services/<name>.py`

A service is a plain Python function. It doesn't know about FastAPI, schemas, or HTTP. It takes inputs, does work, returns a result.

```python
def do_something(name: str, count: int) -> dict:
    # do the work
    return {"result": name * count}
```

**Checklist:**
- Does it import FastAPI? It shouldn't.
- Does it mention Request or Response? It shouldn't.
- Can you call it from a test without starting a server? It should.

---

## How to Write a Schema

File: `app/schemas/<name>.py`

A schema defines the **shape** of data — what fields exist, what types they are, and what constraints they have. Pydantic validates automatically; you don't write if/else checks.

```python
from pydantic import BaseModel, Field

class MyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    count: int = Field(gt=0)

class MyResponse(BaseModel):
    message: str
    id: int
```

### Validation with Field — Your Security Layer

`Field` lets you set rules. If the input breaks a rule, FastAPI returns 422 automatically.

| Constraint | What it does | Example |
|---|---|---|
| `min_length=1` | String can't be empty | `Field(min_length=1)` |
| `max_length=500` | String can't exceed 500 chars | `Field(max_length=500)` |
| `gt=0` | Number must be greater than 0 | `Field(gt=0)` |
| `ge=0` | Number must be >= 0 | `Field(ge=0)` |
| `lt=100` | Number must be less than 100 | `Field(lt=100)` |
| `le=100` | Number must be <= 100 | `Field(le=100)` |

You can combine them: `Field(min_length=1, max_length=500)`

**When you don't use Field:** the field is required but accepts any value of that type — including empty strings.

**When you use Field:** you control exactly what's allowed. Think of it as input sanitization at the gate.

### Request vs Response

- **Request** = what the user sends you. Validate strictly.
- **Response** = what you send back. No validation needed, just shape.

---

## How to Write a Route

File: `app/api/routes.py`

A route connects an HTTP method + URL path to a function. It's the glue between the outside world and your services.

```python
@router.post("/my-endpoint", response_model=MyResponse)
def my_endpoint(payload: MyRequest) -> MyResponse:
    result = do_something(payload.name, payload.count)
    return MyResponse(message="Done", id=result)
```

**The flow:**
1. User sends JSON → FastAPI parses it into `MyRequest`
2. If validation fails → FastAPI returns 422 (you don't write this code)
3. If validation passes → your function runs
4. You call the service, build a response, return it

**Checklist:**
- Does the function do complex logic? Move it to a service.
- Are you validating manually with if/else? Move it to the schema with Field.
- Are you writing try/except for missing fields? Pydantic handles this.

---

## How to Write a Test

File: `tests/test_<name>.py`

### The pattern: Arrange → Act → Assert

```python
def test_save_note_returns_positive_id():
    # Arrange — set up inputs
    book = "My Book"
    chapter = 1
    note = "A thought"

    # Act — call the function
    result = save_note(book, chapter, note)

    # Assert — check the output
    assert result > 0
```

### Test naming — say what you're proving

```
test_<what>_<expected_behavior>
```

Good: `test_save_note_returns_id_of_new_row`
Bad: `test_save_note` (what about it?)
Bad: `test_it_works` (what is "it"?)

Read the name without reading the body. If you can't tell what it proves, rename it.

### Testing API endpoints

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_notes_endpoint_returns_200_for_valid_input():
    response = client.post("/notes", json={
        "book_name": "Test Book",
        "chapter_number": 1,
        "note_text": "A note"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Note saved"

def test_notes_endpoint_rejects_empty_book_name():
    response = client.post("/notes", json={
        "book_name": "",
        "chapter_number": 1,
        "note_text": "A note"
    })
    assert response.status_code == 422
```

### Testing with a temporary database

Your tests should NOT touch the real `data/notes.db`. Use pytest's `tmp_path` and `monkeypatch`:

```python
def test_save_note_stores_data(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("app.services.note_store.DB_PATH", str(db_path))

    init_db()
    note_id = save_note("My Book", 1, "My note")

    import sqlite3
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT * FROM notes").fetchall()
    conn.close()
    assert len(rows) == 1
    assert note_id == 1
```

**What is `monkeypatch`?** It temporarily replaces a value in your code during a test. When the test ends, the original value comes back. This lets you redirect the database path to a temp folder so tests don't pollute your real data.

**What is `tmp_path`?** Pytest creates a temporary folder for each test and deletes it after. You get a clean environment every time.

---

## SQLite — Your Database

SQLite is a file-based database. No server, no setup. Just a `.db` file.

### The basics

```python
import sqlite3

# 1. Connect (creates the file if it doesn't exist)
connection = sqlite3.connect("data/notes.db")

# 2. Do something
connection.execute("SQL HERE")

# 3. If you changed data (INSERT/UPDATE/DELETE), commit
connection.commit()

# 4. Always close when done
connection.close()
```

### Why commit?

Changes aren't saved until you call `commit()`. If you `close()` without `commit()`, your INSERT is lost. Think of it as "save file" — you can type all you want, but until you hit save, it's not permanent.

### Common SQL

**Create a table (run once at startup):**
```sql
CREATE TABLE IF NOT EXISTS my_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
```
- `PRIMARY KEY AUTOINCREMENT` = SQLite assigns the id for you
- `NOT NULL` = this field can't be empty
- `DEFAULT CURRENT_TIMESTAMP` = auto-fills with current time

**Insert:**
```sql
INSERT INTO my_table (name) VALUES (?)
```
```python
cursor = connection.execute("INSERT INTO my_table (name) VALUES (?)", (name,))
new_id = cursor.lastrowid  # the auto-generated id
```

**Select all:**
```python
rows = connection.execute("SELECT * FROM notes").fetchall()
# rows is a list of tuples: [(1, "book", 1, "note", "2026-..."), ...]
```

**Select with filter:**
```python
rows = connection.execute("SELECT * FROM notes WHERE book = ?", (book_name,)).fetchall()
```

**Delete:**
```python
connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
```

### NEVER do this:
```python
# BAD — SQL injection risk
connection.execute(f"SELECT * FROM notes WHERE book = '{user_input}'")
```

### ALWAYS do this:
```python
# GOOD — parameterized query, safe
connection.execute("SELECT * FROM notes WHERE book = ?", (user_input,))
```

The `?` placeholder is how you stay safe. SQLite handles escaping. As a security engineer, this should be automatic for you.

### Read the database from terminal

```bash
.venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('data/notes.db')
rows = conn.execute('SELECT * FROM notes').fetchall()
for row in rows:
    print(row)
conn.close()
"
```

---

## FastAPI — Running and Testing Your API

### Start the server
```bash
.venv/bin/uvicorn app.main:app --reload
```
`--reload` means it restarts automatically when you save a file.

### Test with curl

**GET:**
```bash
curl http://127.0.0.1:8000/health
```

**POST:**
```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H 'Content-Type: application/json' \
  -d '{"book_name": "My Book", "chapter_number": 1, "note_text": "My note"}'
```

**Tip:** Use single quotes around the `-d` value to avoid bash escaping issues with `!` and other special characters.

### Auto-generated docs

Visit `http://127.0.0.1:8000/docs` while the server is running. FastAPI builds interactive API docs from your schemas automatically. You can test endpoints right in the browser.

---

## pytest — Running Tests

```bash
# Run everything
.venv/bin/pytest -q

# Run one file
.venv/bin/pytest tests/test_api.py -v

# Run one specific test
.venv/bin/pytest tests/test_api.py::test_health_returns_200 -v

# Run tests matching a keyword
.venv/bin/pytest -k "notes" -v
```

---

## Git — Saving Your Work

```bash
# See what changed
git status
git diff

# Stage specific files
git add file1.py file2.py

# Commit with a message
git commit -m "Short description of what and why"

# Push to GitHub
git push origin main
```

**Commit messages:** Say what you did and why in one line. Not "updated file" — that says nothing. "Add input validation to notes schema" tells the story.

---

## Debugging Checklist

When something breaks, go through this in order:

1. **Read the error message.** The last line usually tells you what's wrong. The lines above tell you where.
2. **What changed recently?** If it worked before, the bug is in what you just changed.
3. **Can you reproduce it?** Run the exact same command/test again.
4. **Isolate it.** Can you call the function directly in Python? Does the error come from the service, the schema, or the route?
5. **Print something.** Add `print(variable)` to see what a value actually is vs what you think it is.
6. **Check types.** Is the variable a string when you expected an int? A None when you expected a dict?

---

## Common Mistakes and Fixes

| Mistake | Fix |
|---|---|
| `connection.commit()` forgotten | Data not saved — always commit after INSERT/UPDATE/DELETE |
| `connection.close()` forgotten | Database stays locked |
| `os.mkdir` with `exist_ok` | Use `os.makedirs` — `mkdir` doesn't support `exist_ok` |
| Commas in class body: `name: str,` | Remove the comma — class fields don't use commas |
| Single-quote string across lines | Use `"""triple quotes"""` |
| `import *` | Never — import only what you need |
| Forgot `return` in route | Endpoint returns `null` |
| `result.something` when result is just a number | Check what the function actually returns |
| Manual validation in routes | Use `Field` in schemas instead |

---

## How to Add Something to This Guide

When you learn something new that you had to ask about, add it here. Format:

```markdown
## Topic Name

One paragraph explaining the concept.

### Example
(code example)

### When to use it
(one sentence)

### Common mistake
(what goes wrong and how to fix it)
```

This guide is yours. Grow it as you grow.
