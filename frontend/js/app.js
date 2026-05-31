const API_BASE =
    window.location.protocol === "file:"
        ? "http://127.0.0.1:8000"
        : window.location.origin;

let editingNoteId = null;
let draggedNoteId = null;
let loadedNotes = [];

async function checkHealth() {
    const dot = document.getElementById("statusDot");
    const text = document.getElementById("statusText");

    try {
        const res = await fetch(`${API_BASE}/health`);

        if (res.ok) {
            dot.classList.add("online");
            text.textContent = "Connected";
        }
    } catch {
        dot.classList.remove("online");
        text.textContent = "Offline";
    }
}

async function loadNoteCount() {
    const res = await fetch(`${API_BASE}/notes/count`);
    const data = await res.json();
    document.getElementById("noteCount").textContent = data.count;
}

function updateShopLinks(bookTitle) {
    const query = encodeURIComponent(bookTitle.trim());
    document.getElementById("amazonLink").href =
        `https://www.amazon.com/s?k=${query}`;
    document.getElementById("blackwellsLink").href =
        `https://blackwells.co.uk/search/results?searchTerm=${query}`;
}

async function loadSimilarBooks(bookTitle) {
    const extras = document.getElementById("libraryExtras");
    const list = document.getElementById("similarList");
    const trimmed = bookTitle.trim();

    if (!trimmed) {
        extras.hidden = true;
        return;
    }

    extras.hidden = false;
    updateShopLinks(trimmed);
    list.innerHTML = "<li>Loading similar books…</li>";

    try {
        const res = await fetch(
            `${API_BASE}/books/similar?book=${encodeURIComponent(trimmed)}`
        );
        const books = await res.json();

        if (books.length === 0) {
            list.innerHTML = "<li>No suggestions found.</li>";
            return;
        }

        list.innerHTML = books.map((b) => `
            <li>
                <div class="similar-title">${escapeHtml(b.title)}</div>
                <div class="similar-author">${escapeHtml(b.author)}</div>
            </li>
        `).join("");
    } catch {
        list.innerHTML = "<li>Could not load similar books.</li>";
    }
}

function selectBook(bookTitle) {
    document.getElementById("bookFilter").value = bookTitle;
    document.getElementById("bookName").value = bookTitle;
    loadNotes();
    loadSimilarBooks(bookTitle);
    highlightSelectedChip(bookTitle);
    updateFilterUI();
}

function clearFilter() {
    document.getElementById("bookFilter").value = "";
    document.getElementById("libraryExtras").hidden = true;
    loadNotes();
    highlightSelectedChip("");
    updateFilterUI();
}

function updateFilterUI() {
    const filter = document.getElementById("bookFilter").value.trim();
    const clearBtn = document.getElementById("clearFilterBtn");
    const subtitle = document.getElementById("notesSubtitle");
    const sort = document.getElementById("noteSort").value;
    const dragHint = document.getElementById("dragHint");

    clearBtn.hidden = !filter;
    subtitle.textContent = filter
        ? `Filtered by “${filter}”`
        : "All notes";

    const dragEnabled = sort === "custom" && !filter;
    dragHint.hidden = !dragEnabled;
    dragHint.textContent = dragEnabled
        ? "Drag notes by the handle to reorder"
        : "Clear filter and choose Custom order to drag notes";
}

function highlightSelectedChip(bookTitle) {
    const selected = bookTitle.trim();

    document.querySelectorAll(".book-tile").forEach((btn) => {
        btn.classList.toggle("selected", btn.dataset.book === selected);
    });
}

function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = "toast show" + (isError ? " error" : "");

    setTimeout(() => toast.classList.remove("show"), 2500);
}

function setComposeMode(mode) {
    const title = document.getElementById("composeTitle");
    const desc = document.getElementById("composeDesc");
    const saveBtn = document.getElementById("saveBtn");
    const cancelBtn = document.getElementById("cancelEditBtn");
    const composePanel = document.querySelector(".compose-panel");

    if (mode === "edit") {
        title.textContent = "Edit note";
        desc.textContent = "Update this note, then save";
        saveBtn.textContent = "Update note";
        cancelBtn.hidden = false;
        composePanel.classList.add("editing");
        return;
    }

    title.textContent = "New note";
    desc.textContent = "150 characters — short and sharp";
    saveBtn.textContent = "Save note";
    cancelBtn.hidden = true;
    composePanel.classList.remove("editing");
    editingNoteId = null;
}

function startEditNote(note) {
    editingNoteId = note.id;
    document.getElementById("bookName").value = note.book;
    document.getElementById("chapter").value = note.chapter;
    document.getElementById("noteText").value = note.note;
    updateCharCount();
    setComposeMode("edit");
    document.querySelector(".zone-compose").scrollIntoView({ behavior: "smooth", block: "start" });
}

function startEdit(noteId) {
    const note = loadedNotes.find((item) => item.id === noteId);
    if (!note) {
        showToast("Could not load note for editing", true);
        return;
    }
    startEditNote(note);
}

function cancelEdit() {
    clearFormAfterSave();
    setComposeMode("create");
}

async function saveNote() {
    const bookName = document.getElementById("bookName").value.trim();
    const chapter = parseInt(document.getElementById("chapter").value, 10);
    const noteText = document.getElementById("noteText").value.trim();

    if (!bookName || !chapter || !noteText) {
        showToast("Fill in all fields", true);
        return;
    }

    const btn = document.getElementById("saveBtn");
    const isEditing = editingNoteId !== null;
    btn.disabled = true;
    btn.textContent = isEditing ? "Updating..." : "Saving...";

    const payload = {
        book_name: bookName,
        chapter_number: chapter,
        note_text: noteText,
    };

    try {
        const res = await fetch(
            isEditing ? `${API_BASE}/notes/${editingNoteId}` : `${API_BASE}/notes`,
            {
                method: isEditing ? "PATCH" : "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }
        );

        if (res.ok) {
            const data = await res.json();
            showToast(isEditing ? `Updated — note #${data.id}` : `Saved — note #${data.id}`);
            if (isEditing) {
                setComposeMode("create");
                document.getElementById("bookName").value = bookName;
            } else {
                clearFormAfterSave();
                document.getElementById("bookName").value = bookName;
            }
            document.getElementById("chapter").value = "";
            document.getElementById("noteText").value = "";
            updateCharCount();
            loadBooks();
            loadNoteCount();
            loadNotes();
        } else {
            const err = await res.json();
            showToast(err.detail?.[0]?.msg || err.detail || "Save failed", true);
        }
    } catch {
        showToast("Could not reach API", true);
    }

    btn.disabled = false;
    btn.textContent = isEditing ? "Update note" : "Save note";
}

async function deleteNote(id) {
    if (!confirm("Delete this note? This cannot be undone.")) {
        return;
    }

    if (editingNoteId === id) {
        cancelEdit();
    }

    try {
        const res = await fetch(`${API_BASE}/notes/${id}`, { method: "DELETE" });

        if (res.ok) {
            showToast("Note deleted");
            loadBooks();
            loadNoteCount();
            loadNotes();
        } else {
            showToast("Delete failed", true);
        }
    } catch {
        showToast("Could not reach API", true);
    }
}

async function loadBooks() {
    const container = document.getElementById("bookLibrary");

    try {
        const res = await fetch(`${API_BASE}/books`);
        const books = await res.json();

        if (books.length === 0) {
            container.innerHTML =
                '<p class="library-empty">No books yet. Save your first note below to start your library.</p>';
            document.getElementById("libraryCount").textContent = "0";
            return;
        }

        document.getElementById("libraryCount").textContent = String(books.length);

                container.innerHTML = "";
                books.forEach((item, index) => {
                    const btn = document.createElement("button");
                    btn.type = "button";
                    btn.className = `book-tile ${BOOK_TILE_COLORS[index % BOOK_TILE_COLORS.length]}`;
                    btn.dataset.book = item.book;
                    btn.dir = "auto";
                    btn.innerHTML = `<span>${escapeHtml(item.book)}</span><span class="count">${item.note_count}</span>`;
            btn.addEventListener("click", () => {
                selectBook(item.book);
            });
                    container.appendChild(btn);
                });

        highlightSelectedChip(document.getElementById("bookFilter").value.trim());
    } catch {
        container.textContent = "Could not load library.";
    }
}

function canDragNotes() {
    const sort = document.getElementById("noteSort").value;
    const bookFilter = document.getElementById("bookFilter").value.trim();
    return sort === "custom" && !bookFilter;
}

const BOOK_TILE_COLORS = [
    "tile-orange",
    "tile-pink",
    "tile-teal",
    "tile-indigo",
    "tile-green",
    "tile-red",
];

const NOTE_THEMES = [
    "note-theme-purple",
    "note-theme-blue",
    "note-theme-amber",
    "note-theme-green",
];

function noteThemeClass(noteId) {
    return NOTE_THEMES[noteId % NOTE_THEMES.length];
}

function renderNoteItem(note, dragEnabled) {
    return `
        <article
            class="note-item ${noteThemeClass(note.id)}${dragEnabled ? " draggable" : ""}"
            data-note-id="${note.id}"
            ${dragEnabled ? 'draggable="true"' : ""}
        >
            ${dragEnabled ? '<span class="drag-handle" aria-hidden="true">⋮⋮</span>' : ""}
            <div class="note-content">
                <div class="note-top">
                    <div class="note-meta">
                        <div class="note-book" dir="auto">${escapeHtml(note.book)}</div>
                        <span class="note-chapter-badge">Ch. ${note.chapter}</span>
                    </div>
                    <span class="note-id">#${note.id}</span>
                </div>
                <div class="note-text" dir="auto">${escapeHtml(note.note)}</div>
                <div class="note-footer">
                    <span class="note-date">${formatDate(note.created_at)}</span>
                    <div class="note-actions">
                        <button type="button" class="btn-related" onclick="findRelatedNotes(${note.id})" title="Find AI connections">✨ Connect</button>
                        <button type="button" class="btn-edit" onclick="startEdit(${note.id})">Edit</button>
                        <button type="button" class="btn-delete" onclick="deleteNote(${note.id})">Delete</button>
                    </div>
                </div>
            </div>
        </article>
    `;
}

function setupDragAndDrop(container) {
    if (!canDragNotes()) {
        return;
    }

    container.querySelectorAll(".note-item.draggable").forEach((item) => {
        item.addEventListener("dragstart", (event) => {
            draggedNoteId = Number(item.dataset.noteId);
            item.classList.add("dragging");
            event.dataTransfer.effectAllowed = "move";
        });

        item.addEventListener("dragend", () => {
            item.classList.remove("dragging");
            draggedNoteId = null;
            container.querySelectorAll(".note-item").forEach((el) => {
                el.classList.remove("drag-over");
            });
        });

        item.addEventListener("dragover", (event) => {
            event.preventDefault();
            event.dataTransfer.dropEffect = "move";
            item.classList.add("drag-over");
        });

        item.addEventListener("dragleave", () => {
            item.classList.remove("drag-over");
        });

        item.addEventListener("drop", async (event) => {
            event.preventDefault();
            item.classList.remove("drag-over");

            const targetId = Number(item.dataset.noteId);
            if (!draggedNoteId || draggedNoteId === targetId) {
                return;
            }

            const items = [...container.querySelectorAll(".note-item")];
            const ids = items.map((el) => Number(el.dataset.noteId));
            const fromIndex = ids.indexOf(draggedNoteId);
            const toIndex = ids.indexOf(targetId);

            if (fromIndex === -1 || toIndex === -1) {
                return;
            }

            ids.splice(fromIndex, 1);
            ids.splice(toIndex, 0, draggedNoteId);

            try {
                const res = await fetch(`${API_BASE}/notes/reorder`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ note_ids: ids }),
                });

                if (res.ok) {
                    loadNotes();
                } else {
                    showToast("Could not reorder notes", true);
                }
            } catch {
                showToast("Could not reach API", true);
            }
        });
    });
}

async function loadNotes() {
    const container = document.getElementById("notesList");
    const badge = document.getElementById("noteCount");
    const bookFilter = document.getElementById("bookFilter").value.trim();
    const sort = document.getElementById("noteSort").value;

    const params = new URLSearchParams();
    if (bookFilter) {
        params.set("book", bookFilter);
    }
    params.set("sort", sort);

    const url = `${API_BASE}/notes?${params.toString()}`;

    try {
        const res = await fetch(url);
        const notes = await res.json();
        loadedNotes = notes;

        badge.textContent = String(notes.length);
        updateFilterUI();

        if (notes.length === 0) {
            const filterActive = Boolean(bookFilter);
            container.innerHTML = filterActive
                ? `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <p class="empty-title">No notes for this book</p>
                    <p>Try another filter or add a note for “${escapeHtml(bookFilter)}”.</p>
                    <div class="empty-action">
                        <button type="button" class="btn-ghost" onclick="clearFilter()">Clear filter</button>
                    </div>
                </div>`
                : `
                <div class="empty-state">
                    <div class="empty-icon">📖</div>
                    <p class="empty-title">Your desk is empty</p>
                    <p>Save your first note — it’ll show up here, colorful and ready to revisit.</p>
                </div>`;
            populateAiNotePicker();
            return;
        }

        const dragEnabled = canDragNotes();
        container.innerHTML = notes.map((note) => renderNoteItem(note, dragEnabled)).join("");
        setupDragAndDrop(container);
        populateAiNotePicker();
    } catch {
        container.innerHTML = '<div class="empty-state">Could not load notes.</div>';
        badge.textContent = "—";
    }
}

function clearForm() {
    document.getElementById("bookName").value = "";
    document.getElementById("chapter").value = "";
    document.getElementById("noteText").value = "";
    updateCharCount();
    setComposeMode("create");
}

function populateAiNotePicker() {
    const select = document.getElementById("aiNotePick");
    const findBtn = document.getElementById("aiFindBtn");
    if (!select || !findBtn) {
        return;
    }

    if (loadedNotes.length === 0) {
        select.innerHTML = '<option value="">Save notes first…</option>';
        select.disabled = true;
        findBtn.disabled = true;
        return;
    }

    select.disabled = false;
    findBtn.disabled = false;
    select.innerHTML = loadedNotes.map((note) => {
        const preview = note.note.length > 42 ? `${note.note.slice(0, 42)}…` : note.note;
        return `<option value="${note.id}">#${note.id} · ${escapeHtml(note.book)} Ch.${note.chapter} — ${escapeHtml(preview)}</option>`;
    }).join("");
}

function findConnectionsFromPicker() {
    const noteId = Number(document.getElementById("aiNotePick").value);
    if (noteId) {
        findRelatedNotes(noteId);
    }
}

function renderSourceNoteCard(note) {
    return `
        <div class="source-note-label">Your starting note</div>
        <div class="source-note-inner ${noteThemeClass(note.id)}">
            <div class="source-note-meta">
                <span class="source-note-book" dir="auto">${escapeHtml(note.book)}</span>
                <span class="note-chapter-badge">Ch. ${note.chapter}</span>
                <span class="note-id">#${note.id}</span>
            </div>
            <p class="source-note-text" dir="auto">${escapeHtml(note.note)}</p>
        </div>`;
}

function highlightSourceNote(noteId) {
    document.querySelectorAll(".note-item").forEach((item) => {
        item.classList.toggle(
            "note-source-highlight",
            noteId !== null && Number(item.dataset.noteId) === noteId,
        );
    });
}

async function findRelatedNotes(noteId) {
    const panel = document.getElementById("relatedPanel");
    const title = document.getElementById("relatedPanelTitle");
    const subtitle = document.getElementById("relatedPanelSub");
    const sourceCard = document.getElementById("sourceNoteCard");
    const container = document.getElementById("relatedResults");
    const source = loadedNotes.find((note) => note.id === noteId);

    const aiPick = document.getElementById("aiNotePick");
    if (aiPick) {
        aiPick.value = String(noteId);
    }

    panel.hidden = false;
    title.textContent = "Finding connections…";
    subtitle.textContent = source
        ? `Comparing note #${noteId} to ${Math.max(loadedNotes.length - 1, 0)} other note(s)`
        : "";
    sourceCard.hidden = !source;
    sourceCard.innerHTML = source ? renderSourceNoteCard(source) : "";
    container.innerHTML = `
        <div class="related-loading-block">
            <div class="ai-spinner" aria-hidden="true"></div>
            <p class="related-loading">AI is reading your notes and looking for themes…</p>
        </div>`;
    highlightSourceNote(noteId);
    panel.scrollIntoView({ behavior: "smooth", block: "nearest" });

    try {
        const res = await fetch(`${API_BASE}/notes/${noteId}/related`, { method: "POST" });

        if (res.status === 404) {
            title.textContent = "Note not found";
            subtitle.textContent = "";
            container.innerHTML = '<p class="related-empty">That note no longer exists.</p>';
            return;
        }

        if (!res.ok) {
            title.textContent = "Something went wrong";
            subtitle.textContent = "";
            container.innerHTML = '<p class="related-empty">Could not load related notes. Try again in a moment.</p>';
            return;
        }

        const data = await res.json();
        const isStub = data.related.some((item) => item.reason.includes("Stub match"));

        title.textContent = data.related.length
            ? `${data.related.length} connection${data.related.length === 1 ? "" : "s"} found`
            : "No connections yet";
        subtitle.textContent = isStub
            ? "Demo mode — add OPENAI_API_KEY on the server for real AI reasons"
            : "Matched by book, topic, or content";

        if (data.related.length === 0) {
            container.innerHTML = `
                <div class="related-empty-block">
                    <p class="related-empty-title">No matches yet</p>
                    <p class="related-empty">Save more notes on this book or related topics — AI needs other notes to compare against.</p>
                </div>`;
            return;
        }

        container.innerHTML = data.related.map((item) => `
            <article class="related-card ${noteThemeClass(item.note_id)}">
                <div class="related-card-top">
                    <span class="related-card-book" dir="auto">${escapeHtml(item.book)}</span>
                    <span class="note-chapter-badge">Ch. ${item.chapter}</span>
                    <span class="note-id">#${item.note_id}</span>
                </div>
                <p class="related-card-text" dir="auto">${escapeHtml(item.note)}</p>
                <div class="related-reason-block">
                    <span class="related-reason-label">Why it matches</span>
                    <p class="related-card-reason">${escapeHtml(item.reason)}</p>
                </div>
                <button type="button" class="btn-edit btn-small" onclick="startEdit(${item.note_id})">Open note</button>
            </article>
        `).join("");
    } catch {
        title.textContent = "Offline";
        subtitle.textContent = "";
        container.innerHTML = '<p class="related-empty">Could not reach API.</p>';
    }
}

function closeRelatedPanel() {
    document.getElementById("relatedPanel").hidden = true;
    highlightSourceNote(null);
}

function clearFormAfterSave() {
    document.getElementById("chapter").value = "";
    document.getElementById("noteText").value = "";
    updateCharCount();
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    const d = new Date(dateStr + "Z");

    return d.toLocaleDateString("en-GB", {
        day: "numeric",
        month: "short",
        year: "numeric",
    }) + " " + d.toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
    });
}

function updateCharCount() {
    const textarea = document.getElementById("noteText");
    const counter = document.getElementById("charCount");
    const len = textarea.value.length;

    counter.textContent = `${len}/150`;
    counter.className = "char-count" + (len > 140 ? " over" : len > 120 ? " warn" : "");
}

document.getElementById("noteText").addEventListener("input", updateCharCount);
document.getElementById("bookFilter").addEventListener("input", () => {
    const book = document.getElementById("bookFilter").value;
    loadNotes();
    loadSimilarBooks(book);
    highlightSelectedChip(book);
    updateFilterUI();
});

document.getElementById("clearFilterBtn").addEventListener("click", clearFilter);
document.getElementById("closeRelatedBtn").addEventListener("click", closeRelatedPanel);
document.getElementById("aiFindBtn").addEventListener("click", findConnectionsFromPicker);
document.getElementById("noteSort").addEventListener("change", loadNotes);

document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        saveNote();
    }
});

checkHealth();
loadBooks();
loadNoteCount();
loadNotes();
updateFilterUI();
