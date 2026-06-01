/**
 * Under-construction pages — loads copy from /data/roadmap.json by ?tool= key.
 */
const CONSTRUCTION_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`;

function getToolKey() {
    return new URLSearchParams(window.location.search).get("tool") || "restriction";
}

function renderRoadmapLinks(roadmap, currentKey) {
    const list = document.getElementById("roadmapLinks");
    if (!list || !roadmap.tracks) {
        return;
    }

    list.innerHTML = roadmap.tracks
        .map((track) => {
            const links = track.toolKeys
                .map((key) => {
                    const item = roadmap.tools[key];
                    if (!item) {
                        return "";
                    }
                    const isHere = key === currentKey ? " is-here" : "";
                    return `<li><a href="/construction.html?tool=${encodeURIComponent(key)}" class="${isHere.trim()}">${item.funnyTitle}</a></li>`;
                })
                .join("");

            return `
                <li class="construction-roadmap-group">
                    <span class="construction-roadmap-track">${track.title}</span>
                    <ul>${links}</ul>
                </li>
            `;
        })
        .join("");
}

async function loadConstructionPage() {
    const toolKey = getToolKey();

    try {
        const res = await fetch(Site.dataUrl("roadmap.json"), { cache: "no-store" });
        if (!res.ok) {
            throw new Error(`Roadmap fetch failed (${res.status})`);
        }

        const roadmap = await res.json();
        const item = roadmap.tools?.[toolKey] || roadmap.tools?.restriction;

        if (item.pageClass) {
            document.body.className = item.pageClass;
        }

        document.title = `${item.funnyTitle} · Under construction`;

        const pageTitle = document.getElementById("constructionPageTitle");
        if (pageTitle) {
            pageTitle.textContent = item.funnyTitle;
        }

        const icon = document.getElementById("constructionIcon");
        if (icon) {
            icon.innerHTML = CONSTRUCTION_ICON;
        }

        const funny = document.getElementById("constructionFunny");
        if (funny) {
            funny.textContent = item.funnyTitle;
        }

        const toolName = document.getElementById("constructionToolName");
        if (toolName) {
            toolName.textContent = item.toolName;
        }

        const tagline = document.getElementById("constructionTagline");
        if (tagline) {
            tagline.textContent = item.tagline;
        }

        const blurb = document.getElementById("constructionBlurb");
        if (blurb) {
            blurb.textContent = item.blurb;
        }

        const goal = document.getElementById("constructionGoal");
        if (goal) {
            goal.textContent = item.goal || "";
        }

        const deliverables = document.getElementById("constructionDeliverables");
        if (deliverables && item.deliverables) {
            deliverables.innerHTML = item.deliverables
                .map((entry) => `<li>${entry}</li>`)
                .join("");
        }

        const status = document.getElementById("constructionStatusText");
        if (status) {
            status.textContent = item.status;
        }

        const back = document.getElementById("constructionBack");
        if (back) {
            back.href = item.backHref || "/";
            back.textContent = item.backLabel || "Back";
        }

        renderRoadmapLinks(roadmap, toolKey);
    } catch (err) {
        console.error("Construction page load failed:", err);
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadConstructionPage);
} else {
    loadConstructionPage();
}
