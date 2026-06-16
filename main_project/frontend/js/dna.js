/**
 * DNA Lab — calls POST /bio/* endpoints.
 * parseFasta strips FASTA headers before sending sequence to API.
 * analyzeDna fires three parallel requests and renders chart from counts.
 */
const API_BASE = window.Site?.apiBase
    || (window.location.protocol === "file:" ? "http://127.0.0.1:8000" : window.location.origin);

const DNA_EXAMPLES = {
    atgc: "ATGCGTACGTTAGCTAGCTAGCTAGCTAGC",
    brca1: "ATGGATTTATCTGCTCTTCGCGTTGAAGAAGTACAAAATGTCATTAATGCTATGCAGAAAATCTTAGAG",
    covid: "ATGTTCGTAATTTGTCTTGTTTTATTGCCGT",
};

function parseFasta(raw) {
    return raw
        .split(/\r?\n/)
        .filter((line) => line.trim() && !line.trim().startsWith(">"))
        .join("")
        .replace(/\s/g, "")
        .toUpperCase();
}

function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = "toast show" + (isError ? " error" : "");

    setTimeout(() => toast.classList.remove("show"), 2500);
}

async function copyTextToClipboard(text) {
    if (!text) {
        showToast("Nothing to copy", true);
        return;
    }
    try {
        await navigator.clipboard.writeText(text);
        showToast("Copied to clipboard");
    } catch {
        showToast("Could not copy", true);
    }
}

function updateDnaCharCount() {
    const textarea = document.getElementById("dnaInput");
    const counter = document.getElementById("dnaCharCount");
    const len = textarea.value.length;

    counter.textContent = `${len}/1000`;
    counter.className = "char-count" + (len > 950 ? " over" : len > 850 ? " warn" : "");
}

function setDnaSequence(sequence) {
    document.getElementById("dnaInput").value = sequence.slice(0, 1000);
    updateDnaCharCount();
}

function loadSelectedExample() {
    const key = document.getElementById("dnaExampleSelect").value;
    if (!key || !DNA_EXAMPLES[key]) {
        return;
    }
    setDnaSequence(DNA_EXAMPLES[key]);
}

function clearDnaInput() {
    document.getElementById("dnaInput").value = "";
    document.getElementById("dnaExampleSelect").value = "";
    document.getElementById("dnaResults").hidden = true;
    document.getElementById("dnaEmpty").hidden = false;
    document.getElementById("dnaError").hidden = true;
    updateDnaCharCount();
}

function renderNucleotideChart(counts) {
    const entries = [
        { letter: "A", count: counts.a },
        { letter: "T", count: counts.t },
        { letter: "G", count: counts.g },
        { letter: "C", count: counts.c },
    ];
    const max = Math.max(...entries.map((item) => item.count), 1);

    document.getElementById("nucleotideChart").innerHTML = entries
        .map((item) => `
            <div class="chart-row">
                <span class="chart-label">${item.letter}</span>
                <div class="chart-bar-track">
                    <div class="chart-bar-fill chart-${item.letter.toLowerCase()}" style="width: ${(item.count / max) * 100}%"></div>
                </div>
                <span class="chart-value">${item.count}</span>
            </div>
        `)
        .join("");
}

async function analyzeDna() {
    const rawInput = document.getElementById("dnaInput").value;
    const dnaString = parseFasta(rawInput);
    const results = document.getElementById("dnaResults");
    const errorEl = document.getElementById("dnaError");
    const btn = document.getElementById("dnaAnalyzeBtn");

    results.hidden = true;
    errorEl.hidden = true;

    if (!dnaString) {
        showToast("Enter a DNA sequence", true);
        return;
    }

    btn.disabled = true;
    btn.textContent = "Analyzing...";

    const requestBody = JSON.stringify({ dna_string: dnaString });
    const headers = { "Content-Type": "application/json" };

    try {
        const [complementRes, countsRes, gcRes] = await Promise.all([
            fetch(`${API_BASE}/bio/reverse-complement`, { method: "POST", headers, body: requestBody }),
            fetch(`${API_BASE}/bio/nucleotide-counts`, { method: "POST", headers, body: requestBody }),
            fetch(`${API_BASE}/bio/gc-content`, { method: "POST", headers, body: requestBody }),
        ]);

        if (!complementRes.ok || !countsRes.ok || !gcRes.ok) {
            const failedRes = complementRes.ok ? (countsRes.ok ? gcRes : countsRes) : complementRes;
            const err = await failedRes.json();
            const detail = err.detail;
            errorEl.textContent =
                typeof detail === "string" ? detail : detail?.[0]?.msg || "Invalid DNA sequence";
            errorEl.hidden = false;
            document.getElementById("dnaEmpty").hidden = false;
            return;
        }

        const complementData = await complementRes.json();
        const countsData = await countsRes.json();
        const gcData = await gcRes.json();

        document.getElementById("reverseComplement").textContent = complementData.reverse_complement;
        document.getElementById("dnaLength").textContent = gcData.length;
        document.getElementById("gcPercent").textContent = `${gcData.gc_percent.toFixed(1)}%`;
        document.getElementById("gcBarFill").style.width = `${Math.min(gcData.gc_percent, 100)}%`;

        renderNucleotideChart(countsData);

        document.getElementById("nucleotideCounts").innerHTML = [
            { letter: "A", count: countsData.a },
            { letter: "T", count: countsData.t },
            { letter: "G", count: countsData.g },
            { letter: "C", count: countsData.c },
        ]
            .map((item) => `
            <li class="nucleotide-item nucleotide-${item.letter.toLowerCase()}">
                <span class="nucleotide-letter">${item.letter}</span>
                <span class="nucleotide-count">${item.count}</span>
            </li>`)
            .join("");

        results.hidden = false;
        document.getElementById("dnaEmpty").hidden = true;
    } catch {
        showToast("Could not reach API", true);
    } finally {
        btn.disabled = false;
        btn.textContent = "Analyze sequence";
    }
}

document.getElementById("dnaAnalyzeBtn").addEventListener("click", analyzeDna);
document.getElementById("dnaCopyComplementBtn").addEventListener("click", () => {
    copyTextToClipboard(document.getElementById("reverseComplement").textContent);
});
document.getElementById("dnaInput").addEventListener("input", updateDnaCharCount);
document.getElementById("dnaExampleSelect").addEventListener("change", loadSelectedExample);
document.getElementById("dnaClearBtn").addEventListener("click", clearDnaInput);
document.getElementById("dnaFileInput").addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
        return;
    }
    const text = await file.text();
    setDnaSequence(parseFasta(text));
    showToast(`Loaded ${file.name}`);
});

updateDnaCharCount();
