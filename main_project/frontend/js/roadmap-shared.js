/**
 * Shared roadmap rendering — used by index teaser, roadmap.html, and lab upcoming pills.
 */
const Roadmap = {
    escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    },

    async fetch() {
        try {
            const res = await fetch(Site.dataUrl("roadmap.json"), { cache: "no-store" });
            if (!res.ok) {
                throw new Error(`Roadmap fetch failed (${res.status})`);
            }
            return await res.json();
        } catch (err) {
            console.error("Roadmap fetch failed:", err);
            return null;
        }
    },

    renderTrackSteps(track, tools) {
        return track.toolKeys
            .map((key) => {
                const tool = tools[key];
                if (!tool) {
                    return "";
                }

                const deliverables = (tool.deliverables || [])
                    .map((entry) => `<li>${Roadmap.escapeHtml(entry)}</li>`)
                    .join("");

                return `
                    <li class="roadmap-step">
                        <span class="roadmap-step-num">${tool.step}</span>
                        <div class="roadmap-step-body">
                            <h5>${Roadmap.escapeHtml(tool.toolName)}</h5>
                            <p class="roadmap-step-goal">${Roadmap.escapeHtml(tool.goal)}</p>
                            <ul class="roadmap-deliverables">${deliverables}</ul>
                        </div>
                    </li>
                `;
            })
            .join("");
    },

    renderBenchCard(toolKey, tool) {
        return `
            <a class="bench-card bench-card-${Roadmap.escapeHtml(tool.track)}" href="/construction.html?tool=${Roadmap.escapeHtml(toolKey)}">
                <span class="bench-card-step">Step ${tool.step}</span>
                <span class="bench-card-badge">Coming next</span>
                <h4>${Roadmap.escapeHtml(tool.funnyTitle)}</h4>
                <p class="bench-card-tool">${Roadmap.escapeHtml(tool.toolName)}</p>
                <p>${Roadmap.escapeHtml(tool.promise)}</p>
            </a>
        `;
    },

    renderUpcomingPills(roadmap, trackId, navEl) {
        if (!navEl || !roadmap) {
            return;
        }

        const track = (roadmap.tracks || []).find((entry) => entry.id === trackId);
        if (!track) {
            return;
        }

        const tools = roadmap.tools || {};
        const pills = track.toolKeys
            .map((key) => {
                const tool = tools[key];
                if (!tool) {
                    return "";
                }

                return `
                    <a href="/construction.html?tool=${Roadmap.escapeHtml(key)}" class="lab-pill lab-pill-soon">
                        <span class="lab-pill-badge">Step ${tool.step}</span>
                        ${Roadmap.escapeHtml(tool.funnyTitle)}
                    </a>
                `;
            })
            .join("");

        navEl.innerHTML = `
            <span class="lab-crosslinks-label">Coming next</span>
            ${pills}
        `;
    },

    renderCompactTeaser(roadmap) {
        const tools = roadmap.tools || {};

        for (const track of roadmap.tracks || []) {
            const el = document.getElementById(`teaser-${track.id}`);
            if (!el) {
                continue;
            }

            const steps = track.toolKeys
                .map((key) => {
                    const tool = tools[key];
                    if (!tool) {
                        return "";
                    }

                    return `
                        <a class="teaser-step" href="/construction.html?tool=${Roadmap.escapeHtml(key)}">
                            <span class="teaser-step-num">${tool.step}</span>
                            ${Roadmap.escapeHtml(tool.toolName)}
                        </a>
                    `;
                })
                .join("");

            el.innerHTML = `
                <p class="teaser-division">${Roadmap.escapeHtml(track.division)}</p>
                <h4 class="teaser-title">${Roadmap.escapeHtml(track.title)}</h4>
                <p class="teaser-vision">${Roadmap.escapeHtml(track.vision)}</p>
                <div class="teaser-steps">${steps}</div>
            `;
        }
    },

    renderFullPage(roadmap) {
        const about = roadmap.about || {};
        const tools = roadmap.tools || {};

        const setText = (id, value) => {
            const el = document.getElementById(id);
            if (el && value) {
                el.textContent = value;
            }
        };

        document.title = `${about.title || "Roadmap"} · Ziv Grinblat`;
        setText("aboutTitle", about.title);
        setText("aboutIntro", about.intro);
        setText("aboutMethod", about.method);
        setText("aboutClosing", about.closing);
        setText("roadmapBandTitle", about.title);

        for (const track of roadmap.tracks || []) {
            const division = document.getElementById(`track-${track.id}`);
            if (!division) {
                continue;
            }

            const divisionLabel = division.querySelector(".roadmap-track-division");
            if (divisionLabel) {
                divisionLabel.textContent = track.division;
            }

            const title = division.querySelector(".roadmap-track-title");
            if (title) {
                title.textContent = track.title;
            }

            const vision = division.querySelector(".roadmap-track-vision");
            if (vision) {
                vision.textContent = track.vision;
            }

            const liveList = division.querySelector(".roadmap-live-list");
            if (liveList) {
                liveList.innerHTML = (track.liveToday || [])
                    .map((item) => `<li>${Roadmap.escapeHtml(item)}</li>`)
                    .join("");
            }

            const steps = division.querySelector(".roadmap-steps");
            if (steps) {
                steps.innerHTML = Roadmap.renderTrackSteps(track, tools);
            }

            const bench = document.getElementById(`bench-${track.id}`);
            if (bench) {
                bench.innerHTML = track.toolKeys
                    .map((key) => (tools[key] ? Roadmap.renderBenchCard(key, tools[key]) : ""))
                    .join("");
            }
        }
    },

    initUpcomingPills() {
        const nav = document.getElementById("upcomingPills");
        if (!nav) {
            return;
        }

        const trackId = nav.dataset.track;
        if (!trackId) {
            return;
        }

        Roadmap.fetch().then((roadmap) => {
            if (roadmap) {
                Roadmap.renderUpcomingPills(roadmap, trackId, nav);
            }
        });
    },
};

window.Roadmap = Roadmap;
