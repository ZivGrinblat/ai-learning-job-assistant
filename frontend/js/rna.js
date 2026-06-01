/**
 * RNA Lab — POST /bio/rna/reverse-complement
 */
const API_BASE = window.Site?.apiBase
    || (window.location.protocol === "file:" ? "http://127.0.0.1:8000" : window.location.origin);

const RNA_EXAMPLES = {
    basic: "UACGUACGUACG",
    mrna: "AUGCUUUGGAAUUGCC",
    trna: "GCAUUUAGC",
};

function parseRnaInput(raw) {
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

function updateRnaCharCount() {
    const textarea = document.getElementById("rnaInput");
    const counter = document.getElementById("rnaCharCount");
    const len = textarea.value.length;
    counter.textContent = `${len}/1000`;
    counter.className = "char-count" + (len > 950 ? " over" : len > 850 ? " warn" : "");
}

function setRnaSequence(sequence) {
    document.getElementById("rnaInput").value = sequence.slice(0, 1000);
    updateRnaCharCount();
}

function loadSelectedExample() {
    const key = document.getElementById("rnaExampleSelect").value;
    if (!key || !RNA_EXAMPLES[key]) {
        return;
    }
    setRnaSequence(RNA_EXAMPLES[key]);
}

function clearRnaInput() {
    document.getElementById("rnaInput").value = "";
    document.getElementById("rnaExampleSelect").value = "";
    document.getElementById("rnaResults").hidden = true;
    document.getElementById("rnaEmpty").hidden = false;
    document.getElementById("rnaError").hidden = true;
    updateRnaCharCount();
}

function showRnaResults(data) {
    document.getElementById("rnaEmpty").hidden = true;
    document.getElementById("rnaResults").hidden = false;
    document.getElementById("rnaInputDisplay").textContent = data.rna_string;
    document.getElementById("rnaComplementDisplay").textContent = data.reverse_complement;
}

async function analyzeRna() {
    const rnaString = parseRnaInput(document.getElementById("rnaInput").value);
    const errorEl = document.getElementById("rnaError");
    const btn = document.getElementById("rnaAnalyzeBtn");

    errorEl.hidden = true;

    if (!rnaString) {
        showToast("Enter an RNA sequence", true);
        return;
    }

    btn.disabled = true;
    btn.textContent = "Computing…";

    try {
        const res = await fetch(`${API_BASE}/bio/rna/reverse-complement`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rna_string: rnaString }),
        });

        if (!res.ok) {
            const err = await res.json();
            const detail = err.detail;
            errorEl.textContent =
                typeof detail === "string" ? detail : detail?.[0]?.msg || "Invalid RNA sequence";
            errorEl.hidden = false;
            document.getElementById("rnaResults").hidden = true;
            document.getElementById("rnaEmpty").hidden = false;
            return;
        }

        showRnaResults(await res.json());
    } catch {
        showToast("Could not reach API", true);
    } finally {
        btn.disabled = false;
        btn.textContent = "Compute reverse complement";
    }
}

document.getElementById("rnaInput").addEventListener("input", updateRnaCharCount);
document.getElementById("rnaExampleSelect").addEventListener("change", loadSelectedExample);
document.getElementById("rnaClearBtn").addEventListener("click", clearRnaInput);
document.getElementById("rnaAnalyzeBtn").addEventListener("click", analyzeRna);
document.getElementById("rnaCopyComplementBtn").addEventListener("click", () => {
    copyTextToClipboard(document.getElementById("rnaComplementDisplay").textContent);
});

updateRnaCharCount();
