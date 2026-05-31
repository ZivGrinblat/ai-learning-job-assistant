/**
 * Shared utilities for notes.html and dna.html.
 * apiBase: same origin in prod, localhost when opening HTML from disk.
 * checkHealth: polls GET /health for the status dot.
 * injectFooter: adds Home / Book Notes / DNA nav on non-portfolio pages.
 */
const Site = {
    apiBase:
        window.location.protocol === "file:"
            ? "http://127.0.0.1:8000"
            : window.location.origin,

    async checkHealth() {
        const dot = document.getElementById("statusDot");
        const text = document.getElementById("statusText");
        if (!dot || !text) {
            return;
        }

        try {
            const res = await fetch(`${this.apiBase}/health`);
            if (res.ok) {
                dot.classList.add("online");
                text.textContent = document.body.classList.contains("portfolio-page")
                    ? "Projects live"
                    : "Connected";
            }
        } catch {
            dot.classList.remove("online");
            text.textContent = "Offline";
        }
    },

    injectFooter() {
        if (document.querySelector(".site-footer-shared")) {
            return;
        }

        const footer = document.createElement("footer");
        footer.className = "site-footer-shared shell";
        footer.innerHTML = `
            <p>&copy; ${new Date().getFullYear()} Ziv Grinblat</p>
            <nav class="site-footer-nav" aria-label="Footer">
                <a href="/">Home</a>
                <a href="/notes.html">Book Notes</a>
                <a href="/dna.html">DNA Lab</a>
            </nav>`;
        document.body.appendChild(footer);
    },
};

window.Site = Site;

if (document.getElementById("statusDot")) {
    Site.checkHealth();
}

if (!document.body.classList.contains("portfolio-page")) {
    Site.injectFooter();
}
