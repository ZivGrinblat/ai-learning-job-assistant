/**
 * Portfolio home (index.html) — loads frontend/data/profile.json.
 */
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function isPlaceholderUrl(url) {
    return !url || url.includes("YOUR-") || url.includes("your-profile");
}

function renderWorkList(profile) {
    const items = [];

    for (const project of profile.projects || []) {
        items.push(`
            <li>
                <a class="work-item" href="${escapeHtml(project.href)}">
                    <span class="work-title">${escapeHtml(project.title)}</span>
                    <span class="work-desc">${escapeHtml(project.description)}</span>
                    <span class="work-meta">Site</span>
                </a>
            </li>
        `);
    }

    for (const repo of profile.githubHighlights || []) {
        items.push(`
            <li>
                <a class="work-item work-item--external" href="${escapeHtml(repo.url)}" target="_blank" rel="noopener noreferrer">
                    <span class="work-title">${escapeHtml(repo.name)}</span>
                    <span class="work-desc">${escapeHtml(repo.description)}</span>
                    <span class="work-meta">GitHub</span>
                </a>
            </li>
        `);
    }

    return items.join("");
}

function renderProfile(profile) {
    document.title = profile.name;
    document.getElementById("profileName").textContent = profile.name;
    document.getElementById("profileRole").textContent = profile.role;
    document.getElementById("profileTagline").textContent = profile.tagline;

    const contactParts = [];

    if (profile.resumeUrl) {
        contactParts.push(`<a href="${escapeHtml(profile.resumeUrl)}" download>Resume</a>`);
    }
    if (profile.email) {
        contactParts.push(`<a href="mailto:${escapeHtml(profile.email)}">Email</a>`);
    }
    if (!isPlaceholderUrl(profile.linkedin)) {
        contactParts.push(
            `<a href="${escapeHtml(profile.linkedin)}" target="_blank" rel="noopener noreferrer">LinkedIn</a>`
        );
    }
    if (!isPlaceholderUrl(profile.github)) {
        contactParts.push(
            `<a href="${escapeHtml(profile.github)}" target="_blank" rel="noopener noreferrer">GitHub</a>`
        );
    }

    document.getElementById("contactRow").innerHTML = contactParts.join('<span class="contact-sep">·</span>');

    document.getElementById("lookingTitle").textContent = profile.lookingFor.title;
    document.getElementById("lookingBody").textContent = profile.lookingFor.body;

    document.getElementById("experienceList").innerHTML = (profile.experience || [])
        .map((job) => `
            <article class="experience-item">
                <div class="experience-item-header">
                    <h3>${escapeHtml(job.role)}</h3>
                    <p class="experience-company">${escapeHtml(job.company)}</p>
                </div>
                <span class="experience-period">${escapeHtml(job.period)}</span>
                <ul class="experience-highlights">
                    ${job.highlights.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
                </ul>
            </article>
        `)
        .join("");

    document.getElementById("skillsList").textContent = profile.skills.items.join(" · ");

    document.getElementById("workList").innerHTML = renderWorkList(profile);
}

async function loadProfile() {
    try {
        const res = await fetch("data/profile.json");
        if (!res.ok) {
            throw new Error("Could not load profile");
        }
        renderProfile(await res.json());
    } catch {
        document.getElementById("profileTagline").textContent =
            "Could not load profile data.";
    }
}

document.getElementById("footerYear").textContent = String(new Date().getFullYear());

loadProfile();
