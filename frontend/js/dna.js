const API_BASE =
    window.location.protocol === "file:"
        ? "http://127.0.0.1:8000"
        : window.location.origin;

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
        const [complementRes, countsRes] = await Promise.all([
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
        ]);

        if (!complementRes.ok || !countsRes.ok) {
            const failedRes = complementRes.ok ? countsRes : complementRes;
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

        document.getElementById("reverseComplement").textContent =
            complementData.reverse_complement;

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
        btn.textContent = "Analyze";
    }
}

checkHealth();
