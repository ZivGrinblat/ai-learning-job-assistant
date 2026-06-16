/**
 * Portfolio home (index.html) — profile from profile.json; roadmap teaser from roadmap.json.
 */
const PROJECT_ICONS = {
    notes: `<svg class="project-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/></svg>`,
    dna: `<svg class="project-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 15c6.667-6 13.333 0 20-6"/><path d="M9 22c1.798-1.998 2.518-3.995 2.807-5.993"/><path d="M15 2c-1.798 1.998-2.518 3.995-2.807 5.993"/><path d="M17 6l-2.5 2.5"/><path d="M14 8l-1-1"/><path d="M7 18l2.5-2.5"/><path d="M3.5 14.5l.5-.5"/><path d="M20 9l.5.5"/><path d="M6.5 12.5l1 1"/><path d="M16.5 10.5l1 1"/><path d="M9 8l1-1"/></svg>`,
    rna: `<svg class="project-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 18h8"/><path d="M3 22h18"/><path d="M14 22a7 7 0 1 0 0-14h-1"/><path d="M9 14h6"/><path d="M9 12a2 2 0 0 1-2-2V6h6v4a2 2 0 0 1-2 2Z"/><path d="M12 6V3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3"/></svg>`,
};

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function isPlaceholderUrl(url) {
    return !url || url.includes("YOUR-") || url.includes("your-profile");
}

function setupSocialLink(element, url) {
    if (!element) {
        return;
    }

    if (isPlaceholderUrl(url)) {
        element.classList.add("social-placeholder");
        element.href = "#";
        element.removeAttribute("target");
        return;
    }

    element.href = url;
    element.classList.remove("social-placeholder");
}

function projectIconMarkup(iconKey) {
    const icon = PROJECT_ICONS[iconKey];
    if (!icon) {
        return "";
    }

    return `<div class="featured-project-icon featured-project-icon-${escapeHtml(iconKey)}">${icon}</div>`;
}

function renderDisplayName(element, fullName) {
    if (!element) {
        return;
    }

    const parts = (fullName || "Portfolio").trim().split(/\s+/);
    const first = parts[0] || "Portfolio";
    const last = parts.slice(1).join(" ");

    if (last) {
        element.innerHTML =
            `<span class="name-first">${escapeHtml(first)}</span> ` +
            `<span class="name-last">${escapeHtml(last)}</span>`;
        return;
    }

    element.textContent = first;
}

function renderProfile(profile) {
    if (!profile || typeof profile !== "object") {
        throw new Error("Invalid profile payload");
    }

    document.title = `${profile.name || "Portfolio"} · Portfolio`;

    const headerRole = document.getElementById("headerRole");
    if (headerRole) {
        headerRole.textContent = profile.role || "Portfolio";
    }

    const profileName = document.getElementById("profileName");
    if (profileName) {
        renderDisplayName(profileName, profile.name || "Portfolio");
    }

    const profileHeadline = document.getElementById("profileHeadline");
    if (profileHeadline) {
        profileHeadline.textContent = profile.headline || profile.tagline || "";
        profileHeadline.classList.remove("is-loading");
    }

    const profilePitch = document.getElementById("profilePitch");
    if (profilePitch) {
        profilePitch.textContent = profile.pitch || "";
    }

    const profileRole = document.getElementById("profileRole");
    if (profileRole) {
        profileRole.textContent = profile.role || "";
    }

    setupSocialLink(document.getElementById("linkedinLink"), profile.linkedin);
    setupSocialLink(document.getElementById("githubLink"), profile.github);

    const emailLink = document.getElementById("emailLink");
    if (emailLink) {
        if (profile.email) {
            emailLink.hidden = false;
            emailLink.href = `mailto:${profile.email}`;
        } else {
            emailLink.hidden = true;
        }
    }

    const resumeLink = document.getElementById("resumeLink");
    if (resumeLink) {
        if (profile.resumeUrl) {
            resumeLink.hidden = false;
            resumeLink.href = profile.resumeUrl;
        } else {
            resumeLink.hidden = true;
        }
    }

    const lookingFor = profile.lookingFor || {};
    const lookingTitle = document.getElementById("lookingTitle");
    if (lookingTitle) {
        lookingTitle.textContent = lookingFor.title || "Open to";
    }

    const lookingBody = document.getElementById("lookingBody");
    if (lookingBody) {
        lookingBody.textContent = lookingFor.body || "";
    }

    const targets = lookingFor.targets || [];
    const lookingTargets = document.getElementById("lookingTargets");
    if (lookingTargets) {
        lookingTargets.innerHTML = targets
            .map((target) => `<li class="target-role">${escapeHtml(target)}</li>`)
            .join("");
    }

    const heroTargets = document.getElementById("heroTargets");
    if (heroTargets) {
        heroTargets.innerHTML = targets
            .map((target) => `<li class="target-role">${escapeHtml(target)}</li>`)
            .join("");
    }

    const experienceList = document.getElementById("experienceList");
    if (experienceList) {
        experienceList.innerHTML = (profile.experience || [])
            .map((job) => `
                <article class="experience-item">
                    <div class="experience-top">
                        <div>
                            <h4>${escapeHtml(job.role || "")}</h4>
                            <p class="experience-company">${escapeHtml(job.company || "")}</p>
                        </div>
                        <span class="experience-period">${escapeHtml(job.period || "")}</span>
                    </div>
                    <ul class="experience-highlights">
                        ${(job.highlights || [])
                            .map((item) => `<li>${escapeHtml(item)}</li>`)
                            .join("")}
                    </ul>
                </article>
            `)
            .join("");
    }

    const skillsHint = document.getElementById("skillsHint");
    if (skillsHint) {
        skillsHint.textContent = profile.skills?.hint || "";
    }

    const skillsList = document.getElementById("skillsList");
    if (skillsList) {
        skillsList.innerHTML = (profile.skills?.items || [])
            .map((skill) => `<li class="skill-chip">${escapeHtml(skill)}</li>`)
            .join("");
    }

    const githubList = document.getElementById("githubList");
    if (githubList) {
        githubList.innerHTML = (profile.githubHighlights || [])
            .map((repo) => `
                <a class="github-card" href="${escapeHtml(repo.url)}" target="_blank" rel="noopener noreferrer">
                    <h4>${escapeHtml(repo.name)}</h4>
                    <p>${escapeHtml(repo.description)}</p>
                    <span class="project-cta">View on GitHub →</span>
                </a>
            `)
            .join("");
    }

    const projectsGrid = document.getElementById("projectsGrid");
    if (projectsGrid) {
        projectsGrid.innerHTML = (profile.projects || [])
            .map((project) => `
                <a class="featured-project" href="${escapeHtml(project.href)}">
                    ${projectIconMarkup(project.icon)}
                    <div class="featured-project-body">
                        ${project.badge ? `<span class="project-badge">${escapeHtml(project.badge)}</span>` : ""}
                        <h4>${escapeHtml(project.title)}</h4>
                        <p>${escapeHtml(project.description)}</p>
                    </div>
                    <span class="featured-project-cta">Open →</span>
                </a>
            `)
            .join("");
    }
}

async function loadProfile() {
    const headline = document.getElementById("profileHeadline");

    try {
        const res = await fetch(Site.dataUrl("profile.json"), { cache: "no-store" });
        if (!res.ok) {
            throw new Error(`Profile fetch failed (${res.status})`);
        }

        renderProfile(await res.json());
    } catch (err) {
        console.error("Profile load failed:", err);
        if (headline) {
            headline.classList.remove("is-loading");
        }

        const projectsGrid = document.getElementById("projectsGrid");
        if (projectsGrid && !projectsGrid.textContent.trim()) {
            projectsGrid.innerHTML =
                '<p class="load-error">Could not load profile data. Serve with uvicorn and open <code>http://127.0.0.1:8000/</code> — do not open the HTML file directly.</p>';
        }
    }
}

function initHome() {
    const footerYear = document.getElementById("footerYear");
    if (footerYear) {
        footerYear.textContent = String(new Date().getFullYear());
    }

    loadProfile();

    Roadmap.fetch().then((roadmap) => {
        if (roadmap) {
            Roadmap.renderCompactTeaser(roadmap);
            return;
        }

        for (const id of ["teaser-notes", "teaser-bioinformatics"]) {
            const el = document.getElementById(id);
            if (el && !el.textContent.trim()) {
                el.innerHTML = '<p class="load-error">Roadmap data unavailable.</p>';
            }
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHome);
} else {
    initHome();
}
