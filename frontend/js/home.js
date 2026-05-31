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

function renderProfile(profile) {
    document.title = `${profile.name} · Portfolio`;
    document.getElementById("headerRole").textContent = profile.role || "Portfolio";
    document.getElementById("profileName").textContent = profile.name;
    document.getElementById("profileTagline").textContent = profile.tagline;
    document.getElementById("profileRole").textContent = profile.role;

    setupSocialLink(document.getElementById("linkedinLink"), profile.linkedin);
    setupSocialLink(document.getElementById("githubLink"), profile.github);

    const emailLink = document.getElementById("emailLink");
    if (emailLink && profile.email) {
        emailLink.hidden = false;
        emailLink.href = `mailto:${profile.email}`;
    }

    const resumeLink = document.getElementById("resumeLink");
    if (resumeLink && profile.resumeUrl) {
        resumeLink.hidden = false;
        resumeLink.href = profile.resumeUrl;
    }

    document.getElementById("lookingTitle").textContent = profile.lookingFor.title;
    document.getElementById("lookingBody").textContent = profile.lookingFor.body;

    const targets = profile.lookingFor.targets || [];
    document.getElementById("lookingTargets").innerHTML = targets
        .map((target) => `<li class="target-role">${escapeHtml(target)}</li>`)
        .join("");

    const heroTargets = document.getElementById("heroTargetRoles");
    if (heroTargets && targets.length) {
        heroTargets.textContent = targets.join(" · ");
    }

    document.getElementById("experienceList").innerHTML = (profile.experience || [])
        .map((job) => `
            <article class="experience-item">
                <div class="experience-top">
                    <div>
                        <h4>${escapeHtml(job.role)}</h4>
                        <p class="experience-company">${escapeHtml(job.company)}</p>
                    </div>
                    <span class="experience-period">${escapeHtml(job.period)}</span>
                </div>
                <ul class="experience-highlights">
                    ${job.highlights.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
                </ul>
            </article>
        `)
        .join("");

    const skillsHint = document.getElementById("skillsHint");
    if (skillsHint) {
        skillsHint.textContent = profile.skills.hint || "";
    }

    document.getElementById("skillsList").innerHTML = profile.skills.items
        .map((skill) => `<li class="skill-chip">${escapeHtml(skill)}</li>`)
        .join("");

    document.getElementById("githubList").innerHTML = (profile.githubHighlights || [])
        .map((repo) => `
            <a class="github-card" href="${escapeHtml(repo.url)}" target="_blank" rel="noopener noreferrer">
                <h4>${escapeHtml(repo.name)}</h4>
                <p>${escapeHtml(repo.description)}</p>
                <span class="project-cta">View on GitHub →</span>
            </a>
        `)
        .join("");

    document.getElementById("projectsGrid").innerHTML = profile.projects
        .map((project) => `
            <a class="project-card" href="${escapeHtml(project.href)}">
                ${project.badge ? `<span class="project-badge">${escapeHtml(project.badge)}</span>` : ""}
                <h4>${escapeHtml(project.title)}</h4>
                <p>${escapeHtml(project.description)}</p>
                <span class="project-cta">Open project →</span>
            </a>
        `)
        .join("");
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
