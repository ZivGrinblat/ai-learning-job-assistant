# Learn JS (project-focused)

Scratch lessons for the Book Notes frontend. **Type the TODO parts yourself** — no copy-paste from the main app.

## Setup

1. Start the API (for fetch lessons):
   ```bash
   uvicorn app.main:app --reload
   ```
2. Open a lesson file in Chrome/Firefox (double-click or drag into browser).
3. Open **DevTools → Console** (and **Network** for fetch lessons).

## Order

| File | Topic |
|------|--------|
| `lesson-01-fetch.html` | `async` / `await` / `fetch` |
| `lesson-02-json.html` | JSON responses & object fields |
| `lesson-03-dom-read.html` | Reading input values |
| `lesson-04-dom-write.html` | Updating the page |
| `lesson-05-events.html` | Clicks & `addEventListener` |
| `lesson-06-map.html` | Lists → HTML with `.map()` |
| `lesson-07-urls.html` | Query strings & `encodeURIComponent` |

## Rules

- Finish the **TODO** sections without opening `frontend/index.html`.
- If stuck 10+ minutes, write what you tried, then ask for a hint (not the full answer).
- When a lesson passes, add one line to `LEARNING_DIARY.md`.

## Done?

When lessons 01–07 are comfortable, rebuild **one** function (`loadBooks` or `showShopLinks`) in scratch before touching the big `index.html` again.
