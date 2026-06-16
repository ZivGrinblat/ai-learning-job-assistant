const API_BASE = window.Site?.apiBase
    || (window.location.protocol === "file:" ? "http://127.0.0.1:8000" : window.location.origin);

let ENZYMES = [];
const SELECTED_ENZYMES = new Set();
let LAST_SCAN = null;

function el(id) {
    return document.getElementById(id);
}

function parseFasta(raw) {
    return raw
        .split(/\r?\n/)
        .filter((line) => line.trim() && !line.trim().startsWith(">"))
        .join("")
        .replace(/\s/g, "")
        .toUpperCase();
}

function showToast(message, isError = false) {
    const toast = el("toast");
    if (!toast) {
        return;
    }
    toast.textContent = message;
    toast.className = "toast show" + (isError ? " error" : "");
    setTimeout(() => toast.classList.remove("show"), 2500);
}

function updateCharCount() {
    const textarea = el("restrictionInput");
    const counter = el("restrictionCharCount");
    if (!textarea || !counter) {
        return;
    }
    const len = textarea.value.length;
    counter.textContent = `${len}/1000`;
    counter.className = "char-count" + (len > 950 ? " over" : len > 850 ? " warn" : "");
}

function renderEnzymeList(filterValue = "") {
    const listEl = el("enzymeList");
    if (!listEl) {
        return;
    }
    const normalizedFilter = filterValue.trim().toLowerCase();
    const filtered = ENZYMES.filter((item) => {
        if (!normalizedFilter) {
            return true;
        }
        return item.name.toLowerCase().includes(normalizedFilter)
            || item.pattern.toLowerCase().includes(normalizedFilter);
    });

    const enzymeCount = el("enzymeCount");
    if (enzymeCount) {
        enzymeCount.textContent = String(filtered.length);
    }
    listEl.innerHTML = filtered
        .map((item) => `
            <label class="enzyme-item">
                <input type="checkbox" value="${item.name}" ${SELECTED_ENZYMES.has(item.name) ? "checked" : ""} />
                <span class="enzyme-item-name">${item.name}</span>
                <span class="enzyme-item-pattern">${item.pattern}</span>
            </label>
        `)
        .join("");

    listEl.querySelectorAll("input[type='checkbox']").forEach((checkbox) => {
        checkbox.addEventListener("change", (event) => {
            const { checked, value } = event.target;
            if (checked) {
                SELECTED_ENZYMES.add(value);
            } else {
                SELECTED_ENZYMES.delete(value);
            }
            syncSelectedCount();
        });
    });
    syncSelectedCount();
}

function getSelectedEnzymes() {
    return Array.from(SELECTED_ENZYMES);
}

function setSelection(checked) {
    document.querySelectorAll("#enzymeList input[type='checkbox']").forEach((checkbox) => {
        checkbox.checked = checked;
    });
    if (checked) {
        ENZYMES.forEach((item) => SELECTED_ENZYMES.add(item.name));
    } else {
        SELECTED_ENZYMES.clear();
    }
    syncSelectedCount();
}

function setSelectionByPredicate(predicate) {
    SELECTED_ENZYMES.clear();
    ENZYMES.forEach((item) => {
        if (predicate(item)) {
            SELECTED_ENZYMES.add(item.name);
        }
    });
    renderEnzymeList(el("enzymeSearchInput")?.value || "");
}

function syncSelectedCount() {
    const selectedCount = el("selectedEnzymeCount");
    if (selectedCount) {
        selectedCount.textContent = String(SELECTED_ENZYMES.size);
    }
}

function clearForm() {
    const input = el("restrictionInput");
    if (input) {
        input.value = "";
    }
    updateCharCount();
    const search = el("enzymeSearchInput");
    if (search) {
        search.value = "";
    }
    const hitsOnly = el("hitsOnlyToggle");
    if (hitsOnly) {
        hitsOnly.checked = false;
    }
    renderEnzymeList("");
    setSelection(false);
    const errorEl = el("restrictionError");
    const results = el("restrictionResults");
    const empty = el("restrictionEmpty");
    if (errorEl) {
        errorEl.hidden = true;
    }
    if (results) {
        results.hidden = true;
    }
    if (empty) {
        empty.hidden = false;
    }
}

function renderResultsTable(sites, hitsOnly) {
    const filteredEntries = Object.entries(sites)
        .filter(([, positions]) => !hitsOnly || positions.length > 0);
    const rows = filteredEntries
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([enzyme, positions]) => {
            const positionsText = positions.length ? positions.join(", ") : "No matches";
            return `
                <tr>
                    <td>${enzyme}</td>
                    <td>${positions.length}</td>
                    <td class="restriction-positions">${positionsText}</td>
                </tr>
            `;
        })
        .join("");
    if (!rows) {
        const tableWrap = el("restrictionMatchesTable");
        if (!tableWrap) {
            return;
        }
        tableWrap.innerHTML = `
            <p class="restriction-empty-table">No enzymes with hits for current filter.</p>
        `;
        return;
    }
    const tableWrap = el("restrictionMatchesTable");
    if (!tableWrap) {
        return;
    }
    tableWrap.innerHTML = `
        <table class="restriction-table">
            <thead>
                <tr>
                    <th>Enzyme</th>
                    <th>Hits</th>
                    <th>Positions (0-based)</th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>
    `;
}

function renderResults(dnaString, selectedCount, sites) {
    const hitsOnly = el("hitsOnlyToggle")?.checked || false;
    LAST_SCAN = { dnaString, selectedCount, sites };

    const totalHits = Object.values(sites).reduce((acc, positions) => acc + positions.length, 0);
    const summary = el("restrictionSummary");
    if (!summary) {
        return;
    }
    summary.innerHTML = `
        <div class="restriction-summary-card">
            <p class="restriction-summary-label">Sequence length</p>
            <p class="restriction-summary-value">${dnaString.length}</p>
        </div>
        <div class="restriction-summary-card">
            <p class="restriction-summary-label">Enzymes scanned</p>
            <p class="restriction-summary-value">${selectedCount}</p>
        </div>
        <div class="restriction-summary-card">
            <p class="restriction-summary-label">Total matches</p>
            <p class="restriction-summary-value">${totalHits}</p>
        </div>
    `;
    renderResultsTable(sites, hitsOnly);
    const results = el("restrictionResults");
    const empty = el("restrictionEmpty");
    if (results) {
        results.hidden = false;
    }
    if (empty) {
        empty.hidden = true;
    }
}

async function loadEnzymeCatalog() {
    try {
        const response = await fetch(`${API_BASE}/bio/dna/restriction-enzymes`);
        if (!response.ok) {
            throw new Error("Unable to load enzyme catalog");
        }
        const data = await response.json();
        ENZYMES = data.enzymes || [];
        const sourceMeta = el("restrictionSourceMeta");
        if (sourceMeta) {
            sourceMeta.innerHTML = `Catalog source: <a href="${data.source}" target="_blank" rel="noopener noreferrer">online enzyme dataset</a> · ${data.count} enzymes loaded`;
        }
        renderEnzymeList("");
    } catch {
        const sourceMeta = el("restrictionSourceMeta");
        if (sourceMeta) {
            sourceMeta.textContent = "Using fallback local enzyme set.";
        }
        showToast("Could not load enzyme catalog", true);
    }
}

async function analyzeRestrictionSites() {
    const btn = el("restrictionAnalyzeBtn");
    const errorEl = el("restrictionError");
    if (!btn || !errorEl) {
        return;
    }
    errorEl.hidden = true;

    const dnaString = parseFasta(el("restrictionInput")?.value || "");
    if (!dnaString) {
        showToast("Enter a DNA sequence", true);
        return;
    }

    const selected = getSelectedEnzymes();
    btn.disabled = true;
    btn.textContent = "Scanning...";
    try {
        const response = await fetch(`${API_BASE}/bio/dna/restriction-sites`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                dna_string: dnaString,
                selected_enzymes: selected.length ? selected : null,
            }),
        });
        if (!response.ok) {
            const err = await response.json();
            const detail = typeof err.detail === "string" ? err.detail : "Scan failed";
            errorEl.textContent = detail;
            errorEl.hidden = false;
            const results = el("restrictionResults");
            const empty = el("restrictionEmpty");
            if (results) {
                results.hidden = true;
            }
            if (empty) {
                empty.hidden = false;
            }
            return;
        }
        const data = await response.json();
        const scannedCount = selected.length || Object.keys(data.sites).length;
        renderResults(data.dna_string, scannedCount, data.sites);
    } catch {
        showToast("Could not reach API", true);
    } finally {
        btn.disabled = false;
        btn.textContent = "Find restriction sites";
    }
}

el("restrictionAnalyzeBtn")?.addEventListener("click", analyzeRestrictionSites);
el("restrictionInput")?.addEventListener("input", updateCharCount);
el("restrictionClearBtn")?.addEventListener("click", clearForm);
el("enzymeSelectAllBtn")?.addEventListener("click", () => setSelection(true));
el("enzymeClearBtn")?.addEventListener("click", () => setSelection(false));
el("presetCommonBtn")?.addEventListener("click", () => {
    const common = new Set(["EcoRI", "HindIII", "BamHI", "NotI", "XhoI", "NheI", "SpeI", "KpnI"]);
    setSelectionByPredicate((item) => common.has(item.name));
});
el("presetSixCuttersBtn")?.addEventListener("click", () => {
    setSelectionByPredicate((item) => item.pattern.length === 6);
});
el("presetRareCuttersBtn")?.addEventListener("click", () => {
    setSelectionByPredicate((item) => item.pattern.length >= 7);
});
el("enzymeSearchInput")?.addEventListener("input", (event) => {
    renderEnzymeList(event.target.value);
});
el("hitsOnlyToggle")?.addEventListener("change", () => {
    if (LAST_SCAN) {
        renderResultsTable(LAST_SCAN.sites, el("hitsOnlyToggle")?.checked || false);
    }
});

updateCharCount();
loadEnzymeCatalog();
