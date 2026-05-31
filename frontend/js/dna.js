const API_BASE =
    window.location.protocol === "file:"
        ? "http://127.0.0.1:8000"
        : window.location.origin;

const DNA_EXAMPLE = "ATGCGTACGTTAGCTAGCTAGCTAGCTAGC";

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

function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = "toast show" + (isError ? " error" : "");

    setTimeout(() => toast.classList.remove("show"), 2500);
}

function updateDnaCharCount() {
    const textarea = document.getElementById("dnaInput");
    const counter = document.getElementById("dnaCharCount");
    const len = textarea.value.length;

    counter.textContent = `${len}/1000`;
    counter.className = "char-count" + (len > 950 ? " over" : len > 850 ? " warn" : "");
}

function loadExampleSequence() {
    document.getElementById("dnaInput").value = DNA_EXAMPLE;
    updateDnaCharCount();
}

async function analyzeDna() {
    const dnaString = document.getElementById("dnaInput").value.trim();
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
            fetch(`${API_BASE}/bio/reverse-complement`, {
                method: "POST",
                headers,
                body: requestBody,
            }),
            fetch(`${API_BASE}/bio/nucleotide-counts`, {
                method: "POST",
                headers,
                body: requestBody,
            }),
            fetch(`${API_BASE}/bio/gc-content`, {
                method: "POST",
                headers,
                body: requestBody,
            }),
        ]);

        if (!complementRes.ok || !countsRes.ok || !gcRes.ok) {
            const failedRes = complementRes.ok
                ? countsRes.ok
                    ? gcRes
                    : countsRes
                : complementRes;
            const err = await failedRes.json();
            const detail = err.detail;
            errorEl.textContent =
                typeof detail === "string"
                    ? detail
                    : detail?.[0]?.msg || "Invalid DNA sequence";
            errorEl.hidden = false;
            return;
        }

        const complementData = await complementRes.json();
        const countsData = await countsRes.json();
        const gcData = await gcRes.json();

        document.getElementById("reverseComplement").textContent =
            complementData.reverse_complement;

        document.getElementById("dnaLength").textContent = gcData.length;
        document.getElementById("gcPercent").textContent =
            `${gcData.gc_percent.toFixed(1)}%`;
        document.getElementById("gcBarFill").style.width =
            `${Math.min(gcData.gc_percent, 100)}%`;

        document.getElementById("nucleotideCounts").innerHTML = [
            { letter: "A", count: countsData.a },
            { letter: "T", count: countsData.t },
            { letter: "G", count: countsData.g },
            { letter: "C", count: countsData.c },
        ]
            .map(
                (item) => `
            <li class="nucleotide-item nucleotide-${item.letter.toLowerCase()}">
                <span class="nucleotide-letter">${item.letter}</span>
                <span class="nucleotide-count">${item.count}</span>
            </li>`
            )
            .join("");

        results.hidden = false;
    } catch {
        showToast("Could not reach API", true);
    } finally {
        btn.disabled = false;
        btn.textContent = "Analyze sequence";
    }
}

document.getElementById("dnaInput").addEventListener("input", updateDnaCharCount);
document.getElementById("dnaExampleBtn").addEventListener("click", loadExampleSequence);

checkHealth();
updateDnaCharCount();
