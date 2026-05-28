# JS from scratch (you type every line)

Throwaway practice. **Do not open `frontend/index.html` until step 06 passes.**

## Before each file

1. Open the HTML in Chrome/Firefox (double-click the file).
2. Open DevTools → **Console** (steps 01–04) or **Console + Network** (05–06).

## Order — one file, one idea

| Step | File | You learn |
|------|------|-----------|
| 01 | `01-dom-text.html` | `document.getElementById`, `.textContent` |
| 02 | `02-click.html` | `addEventListener`, function vs `function()` |
| 03 | `03-read-input.html` | `.value` on `<input>` |
| 04 | `04-const-template.html` | `const`, `` `backticks` ``, `${}` |
| 05 | `05-fetch-health.html` | `async`, `await`, `fetch`, `res.json()` |
| 06 | `06-try-catch.html` | `try` / `catch`, `res.ok` |

## Rules

- Fill only the `// TODO` blocks. The rest is scaffolding — leave it unless the comment says otherwise.
- If stuck 10+ minutes: write what you tried, what you expected, what happened. Ask for a **hint**, not the answer.
- **Pass** = the "Done when" line in each file works.
- When step 06 passes, you rebuild `pingApi` in step 05 **from memory** once, then you're allowed to read one function in `frontend/index.html`.

## API (steps 05–06 only)

```bash
uvicorn app.main:app --reload
```
