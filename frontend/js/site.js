/**
 * Shared utilities for all site pages.
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
                text.textContent = "Online";
            }
        } catch {
            dot.classList.remove("online");
            text.textContent = "Offline";
        }
    },

    setFooterYear() {
        const yearEl = document.getElementById("footerYear");
        if (yearEl) {
            yearEl.textContent = String(new Date().getFullYear());
        }
    },
};

window.Site = Site;

Site.setFooterYear();

if (document.getElementById("statusDot")) {
    Site.checkHealth();
}
