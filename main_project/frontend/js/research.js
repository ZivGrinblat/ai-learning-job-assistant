const API_BASE = window.Site?.apiBase
    || (window.location.protocol === "file:" ? "http://127.0.0.1:8000" : window.location.origin);

const ARTICLE_MAX = 12000;
const ARTICLE_MIN = 50;
const SAMPLE_ARTICLES = {
    security: {
        title: "Hardening ML Pipelines with Threat Modeling",
        text: "Machine-learning pipelines are vulnerable at ingestion, feature engineering, model training, and deployment. "
            + "A structured threat model identifies trust boundaries, attacker capabilities, and high-value assets. "
            + "The article compares data poisoning controls, model artifact signing, and deployment policy enforcement. "
            + "It highlights tradeoffs between velocity and verifiability in production teams. "
            + "A practical recommendation is to map one end-to-end pipeline and define minimum integrity signals for each stage.",
        focus: "security",
    },
    bio: {
        title: "Benchmarking Restriction Site Detection Across Enzyme Sets",
        text: "Restriction site analysis quality depends on enzyme catalog completeness, pattern interpretation, and clear reporting. "
            + "The article evaluates matching behavior on ambiguous IUPAC patterns and compares deterministic scanning methods. "
            + "It also discusses usability concerns: how to present high-cardinality enzyme results without overwhelming users. "
            + "The paper recommends exposing transparent algorithm assumptions and adding quality checks for input DNA validation.",
        focus: "bio",
    },
    ai: {
        title: "From Summaries to Actionable Research Agendas",
        text: "Most AI writing tools summarize text but fail to convert reading into execution plans. "
            + "This article proposes structured pathway generation where each output includes rationale, complexity, and first action. "
            + "The authors show improved follow-through when pathways are specific, bounded, and linked to concrete search queries. "
            + "They emphasize strict output schemas and fallback behavior for resilience.",
        focus: "ai",
    },
};

let LAST_RESULT = null;

function el(id) {
    return document.getElementById(id);
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

function updateArticleCount() {
    const textEl = el("researchArticleText");
    const countEl = el("researchCharCount");
    const quality = el("researchQualityBadge");
    if (!textEl || !countEl || !quality) {
        return;
    }
    const len = textEl.value.length;
    countEl.textContent = `${len}/${ARTICLE_MAX}`;
    countEl.className = "char-count" + (len > 11500 ? " over" : len > 10000 ? " warn" : "");

    if (len < ARTICLE_MIN) {
        quality.textContent = "Input too short";
        quality.classList.remove("good");
    } else if (len < 300) {
        quality.textContent = "Usable input";
        quality.classList.remove("good");
    } else {
        quality.textContent = "High quality input";
        quality.classList.add("good");
    }
}

function clearResearchForm() {
    el("researchTitle").value = "";
    el("researchSourceUrl").value = "";
    el("researchFocus").value = "general";
    el("researchPathCount").value = "5";
    el("researchExampleSelect").value = "";
    el("researchArticleText").value = "";
    el("difficultyFilter").value = "all";
    el("researchError").hidden = true;
    el("researchResults").hidden = true;
    el("researchEmpty").hidden = false;
    LAST_RESULT = null;
    updateArticleCount();
}

function applySample(sampleKey) {
    const sample = SAMPLE_ARTICLES[sampleKey];
    if (!sample) {
        return;
    }
    el("researchTitle").value = sample.title;
    el("researchFocus").value = sample.focus;
    el("researchArticleText").value = sample.text;
    updateArticleCount();
}

function filteredPathways(pathways) {
    const difficulty = el("difficultyFilter").value;
    if (difficulty === "all") {
        return pathways;
    }
    return pathways.filter((item) => item.difficulty === difficulty);
}

function difficultyBadge(difficulty) {
    return `<span class="research-badge ${difficulty}">${difficulty}</span>`;
}

function renderPathways(pathways) {
    const list = el("researchPathwaysList");
    const visible = filteredPathways(pathways);
    if (!visible.length) {
        list.innerHTML = `<div class="research-empty-inline">No pathways match this difficulty filter.</div>`;
        return;
    }
    list.innerHTML = visible.map((item, index) => `
        <article class="research-pathway-card">
            <div class="research-pathway-head">
                <h3 class="research-pathway-title">${index + 1}. ${item.title}</h3>
                ${difficultyBadge(item.difficulty)}
            </div>
            <div class="research-field">
                <p class="research-field-label">Why it matters</p>
                <p class="research-field-value">${item.why_it_matters}</p>
            </div>
            <div class="research-field">
                <p class="research-field-label">First step</p>
                <p class="research-field-value">${item.first_step}</p>
            </div>
            <div class="research-field">
                <p class="research-field-label">Search queries</p>
                <div class="research-queries">
                    ${item.search_queries.map((query) => `<button type="button" class="research-query-chip" data-query="${query.replace(/"/g, "&quot;")}">${query}</button>`).join("")}
                </div>
            </div>
        </article>
    `).join("");

    list.querySelectorAll(".research-query-chip").forEach((chip) => {
        chip.addEventListener("click", () => {
            const query = chip.dataset.query || "";
            navigator.clipboard.writeText(query)
                .then(() => showToast("Query copied"))
                .catch(() => showToast("Could not copy query", true));
        });
    });
}

function renderResearchResult(data) {
    LAST_RESULT = data;
    el("researchSummaryText").textContent = data.article_summary;
    renderPathways(data.pathways);
    el("researchResults").hidden = false;
    el("researchEmpty").hidden = true;
}

async function generateResearchPathways() {
    const btn = el("generatePathwaysBtn");
    const error = el("researchError");
    const articleText = el("researchArticleText").value.trim();
    const focus = el("researchFocus").value;
    const pathwaysCount = Number(el("researchPathCount").value);
    error.hidden = true;

    if (articleText.length < ARTICLE_MIN) {
        error.textContent = `Article text must be at least ${ARTICLE_MIN} characters.`;
        error.hidden = false;
        return;
    }

    btn.disabled = true;
    btn.textContent = "Generating...";
    try {
        const response = await fetch(`${API_BASE}/research/pathways`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                article_text: articleText,
                focus_area: focus,
                pathways_count: pathwaysCount,
            }),
        });
        if (!response.ok) {
            const err = await response.json();
            const detail = typeof err.detail === "string" ? err.detail : "Could not generate pathways.";
            error.textContent = detail;
            error.hidden = false;
            return;
        }
        const data = await response.json();
        renderResearchResult(data);
    } catch {
        showToast("Could not reach API", true);
    } finally {
        btn.disabled = false;
        btn.textContent = "Generate pathways";
    }
}

function buildMarkdown(result) {
    const title = el("researchTitle").value.trim();
    const source = el("researchSourceUrl").value.trim();
    const focus = el("researchFocus").value;
    const lines = [];
    lines.push("# Research Pathways Report");
    lines.push("");
    if (title) {
        lines.push(`- Title: ${title}`);
    }
    if (source) {
        lines.push(`- Source: ${source}`);
    }
    lines.push(`- Focus: ${focus}`);
    lines.push(`- Generated pathways: ${result.pathways.length}`);
    lines.push("");
    lines.push("## Summary");
    lines.push(result.article_summary);
    lines.push("");
    lines.push("## Pathways");
    result.pathways.forEach((item, idx) => {
        lines.push(`### ${idx + 1}. ${item.title}`);
        lines.push(`- Difficulty: ${item.difficulty}`);
        lines.push(`- Why it matters: ${item.why_it_matters}`);
        lines.push(`- First step: ${item.first_step}`);
        lines.push(`- Search queries: ${item.search_queries.join(" | ")}`);
        lines.push("");
    });
    return lines.join("\n");
}

function downloadText(filename, content, mime = "text/plain") {
    const blob = new Blob([content], { type: `${mime};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}

function copyResearchReport() {
    if (!LAST_RESULT) {
        showToast("Generate a report first", true);
        return;
    }
    const report = buildMarkdown(LAST_RESULT);
    navigator.clipboard.writeText(report)
        .then(() => showToast("Report copied"))
        .catch(() => showToast("Could not copy report", true));
}

function downloadResearchMarkdown() {
    if (!LAST_RESULT) {
        showToast("Generate a report first", true);
        return;
    }
    downloadText("research-pathways.md", buildMarkdown(LAST_RESULT), "text/markdown");
}

function downloadResearchJson() {
    if (!LAST_RESULT) {
        showToast("Generate a report first", true);
        return;
    }
    downloadText("research-pathways.json", JSON.stringify(LAST_RESULT, null, 2), "application/json");
}

el("researchArticleText")?.addEventListener("input", updateArticleCount);
el("clearResearchBtn")?.addEventListener("click", clearResearchForm);
el("researchExampleSelect")?.addEventListener("change", (event) => applySample(event.target.value));
el("generatePathwaysBtn")?.addEventListener("click", generateResearchPathways);
el("difficultyFilter")?.addEventListener("change", () => {
    if (LAST_RESULT) {
        renderPathways(LAST_RESULT.pathways);
    }
});
el("copyResearchReportBtn")?.addEventListener("click", copyResearchReport);
el("downloadResearchMarkdownBtn")?.addEventListener("click", downloadResearchMarkdown);
el("downloadResearchJsonBtn")?.addEventListener("click", downloadResearchJson);

updateArticleCount();
