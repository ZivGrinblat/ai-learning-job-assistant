/**
 * Full roadmap page (roadmap.html).
 */
function initRoadmapPage() {
    const yearEl = document.getElementById("footerYear");
    if (yearEl) {
        yearEl.textContent = String(new Date().getFullYear());
    }

    Roadmap.fetch().then((roadmap) => {
        if (roadmap) {
            Roadmap.renderFullPage(roadmap);
            return;
        }

        const intro = document.getElementById("aboutIntro");
        if (intro) {
            intro.textContent =
                "Could not load roadmap.json. Serve with uvicorn (http://127.0.0.1:8000/roadmap.html) or deploy the file from frontend/data/.";
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRoadmapPage);
} else {
    initRoadmapPage();
}
