const SEO_DEFAULTS = (() => {
    const pickMeta = (selector) => {
        const el = document.querySelector(selector);
        return el ? el.getAttribute("content") || "" : "";
    };
    const ld = document.getElementById("seo-jsonld");
    return {
        title: document.title,
        description: pickMeta('meta[name="description"]'),
        keywords: pickMeta('meta[name="keywords"]'),
        canonical: (() => {
            const el = document.querySelector('link[rel="canonical"]');
            return el ? el.getAttribute("href") || "" : "";
        })(),
        ogTitle: pickMeta('meta[property="og:title"]'),
        ogDesc: pickMeta('meta[property="og:description"]'),
        ogUrl: pickMeta('meta[property="og:url"]'),
        twTitle: pickMeta('meta[name="twitter:title"]'),
        twDesc: pickMeta('meta[name="twitter:description"]'),
        jsonLd: ld ? ld.textContent.trim() : "",
    };
})();

function setMetaContent(selector, value) {
    const el = document.querySelector(selector);
    if (el && "content" in el) {
        el.setAttribute("content", value);
    }
}

function setLinkHref(rel, value) {
    const el = document.querySelector(`link[rel="${rel}"]`);
    if (el) {
        el.setAttribute("href", value);
    }
}

function resetSeoToDefaults() {
    document.title = SEO_DEFAULTS.title;
    setMetaContent('meta[name="description"]', SEO_DEFAULTS.description);
    setMetaContent('meta[name="keywords"]', SEO_DEFAULTS.keywords);
    setLinkHref("canonical", SEO_DEFAULTS.canonical);
    setMetaContent('meta[property="og:title"]', SEO_DEFAULTS.ogTitle);
    setMetaContent('meta[property="og:description"]', SEO_DEFAULTS.ogDesc);
    setMetaContent('meta[property="og:url"]', SEO_DEFAULTS.ogUrl);
    setMetaContent('meta[name="twitter:title"]', SEO_DEFAULTS.twTitle);
    setMetaContent('meta[name="twitter:description"]', SEO_DEFAULTS.twDesc);
    const ld = document.getElementById("seo-jsonld");
    if (ld && SEO_DEFAULTS.jsonLd) {
        ld.textContent = SEO_DEFAULTS.jsonLd;
    }
    if (window.history && window.history.replaceState) {
        window.history.replaceState(null, "", window.location.pathname || "/");
    }
}

function applyDynamicSeo(seo) {
    if (!seo || !seo.apply) {
        resetSeoToDefaults();
        return;
    }
    document.title = seo.title;
    setMetaContent('meta[name="description"]', seo.description);
    setMetaContent('meta[name="keywords"]', seo.keywords);
    setLinkHref("canonical", seo.canonical);
    setMetaContent('meta[property="og:title"]', seo.og_title);
    setMetaContent('meta[property="og:description"]', seo.og_description);
    setMetaContent('meta[property="og:url"]', seo.canonical);
    setMetaContent('meta[name="twitter:title"]', seo.twitter_title);
    setMetaContent('meta[name="twitter:description"]', seo.twitter_description);
    const ld = document.getElementById("seo-jsonld");
    if (ld && seo.json_ld) {
        try {
            const parsed = JSON.parse(seo.json_ld);
            ld.textContent = JSON.stringify(parsed, null, 2);
        } catch {
            ld.textContent = seo.json_ld;
        }
    }
    if (!window.history || !window.history.replaceState) {
        return;
    }
    const u = new URL(window.location.href);
    if (seo.profile_id != null) {
        u.searchParams.set("mode", "characteristic");
        u.searchParams.set("profile_id", String(seo.profile_id));
        u.searchParams.delete("source_id");
        u.searchParams.delete("target_id");
        window.history.replaceState(null, "", `${u.pathname}?${u.searchParams.toString()}`);
        return;
    }
    if (seo.source_id != null && seo.target_id != null) {
        u.searchParams.set("mode", "relationship");
        u.searchParams.set("source_id", String(seo.source_id));
        u.searchParams.set("target_id", String(seo.target_id));
        u.searchParams.delete("profile_id");
        window.history.replaceState(null, "", `${u.pathname}?${u.searchParams.toString()}`);
    }
}

const modeSelect = document.getElementById("mode-select");
const step2Characteristic = document.getElementById("step-2-characteristic");
const step2Relationship = document.getElementById("step-2-relationship");
const profileSelect = document.getElementById("profile-select");
const sourceSelect = document.getElementById("source-select");
const targetSelect = document.getElementById("target-select");
const showCharacteristicBtn = document.getElementById("show-characteristic-btn");
const showRelationshipBtn = document.getElementById("show-relationship-btn");
const resultCard = document.getElementById("result-card");
const resultTitle = document.getElementById("result-title");
const resultContent = document.getElementById("result-content");

let selectedMode = "";

const resetSelect = (el, text) => {
    el.innerHTML = `<option value="">${text}</option>`;
};

modeSelect.addEventListener("change", async (e) => {
    selectedMode = e.target.value;
    resetSeoToDefaults();
    resultCard.classList.add("hidden");
    resetSelect(profileSelect, "Выберите профиль");
    resetSelect(sourceSelect, "Выберите первый профиль");
    resetSelect(targetSelect, "Сначала выберите профиль 1");

    step2Characteristic.classList.add("hidden");
    step2Relationship.classList.add("hidden");

    if (!selectedMode) return;

    const resp = await fetch(`/api/options/?mode=${selectedMode}`);
    const data = await resp.json();

    if (selectedMode === "characteristic") {
        data.items.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.label;
            profileSelect.appendChild(opt);
        });
        step2Characteristic.classList.remove("hidden");
        return;
    }

    data.items.forEach((item) => {
        const opt = document.createElement("option");
        opt.value = item.id;
        opt.textContent = item.label;
        sourceSelect.appendChild(opt);
    });
    step2Relationship.classList.remove("hidden");
});

sourceSelect.addEventListener("change", async () => {
    resultCard.classList.add("hidden");
    resetSelect(targetSelect, "Выберите второй профиль");
    if (!sourceSelect.value) return;
    const resp = await fetch(`/api/relationship-targets/?source_id=${sourceSelect.value}`);
    const data = await resp.json();
    data.items.forEach((item) => {
        const opt = document.createElement("option");
        opt.value = item.id;
        opt.textContent = item.label;
        targetSelect.appendChild(opt);
    });
});

const renderNiceMarkdown = (md) => {
    return marked.parse((md || "").trim());
};

const stylizeRelationshipMarkup = () => {
    const lists = resultContent.querySelectorAll("ul");
    lists.forEach((ul) => {
        ul.classList.add("relation-list");
    });

    const listItems = resultContent.querySelectorAll("li");
    listItems.forEach((li) => {
        li.classList.add("relation-item");
        const html = li.innerHTML.trim();
        const match = html.match(/^<strong>([^<]+):<\/strong>\s*(.*)$/i);
        if (!match) return;

        const [, label, value] = match;
        li.innerHTML = `
            <div class="relation-label">${label}</div>
            <div class="relation-value">${value}</div>
        `;
    });
};

const showResult = async (url) => {
    const resp = await fetch(url);
    const data = await resp.json();
    resultTitle.textContent = data.title;

    if (data.seo) {
        applyDynamicSeo(data.seo);
    } else {
        resetSeoToDefaults();
    }

    resultContent.classList.remove("relationship-view", "characteristic-view");
    if (data.type === "relationship") {
        resultContent.classList.add("relationship-view");
    } else {
        resultContent.classList.add("characteristic-view");
    }

    resultContent.innerHTML = renderNiceMarkdown(data.content_markdown);
    if (data.type === "relationship") {
        stylizeRelationshipMarkup();
    }
    resultCard.classList.remove("hidden");
};

showCharacteristicBtn.addEventListener("click", async () => {
    if (!profileSelect.value) return;
    await showResult(`/api/result/?mode=characteristic&profile_id=${profileSelect.value}`);
});

showRelationshipBtn.addEventListener("click", async () => {
    if (!sourceSelect.value || !targetSelect.value) return;
    await showResult(`/api/result/?mode=relationship&source_id=${sourceSelect.value}&target_id=${targetSelect.value}`);
});

document.addEventListener("DOMContentLoaded", async () => {
    const p = new URLSearchParams(window.location.search);
    const mode = p.get("mode");

    if (mode === "characteristic") {
        const id = p.get("profile_id");
        if (!id) return;
        modeSelect.value = "characteristic";
        selectedMode = "characteristic";
        step2Relationship.classList.add("hidden");
        resultCard.classList.add("hidden");
        resetSelect(profileSelect, "Выберите профиль");
        const resp = await fetch("/api/options/?mode=characteristic");
        const data = await resp.json();
        data.items.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.label;
            profileSelect.appendChild(opt);
        });
        step2Characteristic.classList.remove("hidden");
        profileSelect.value = id;
        if (!profileSelect.value) return;
        await showResult(`/api/result/?mode=characteristic&profile_id=${encodeURIComponent(id)}`);
        return;
    }

    if (mode === "relationship") {
        const sid = p.get("source_id");
        const tid = p.get("target_id");
        if (!sid || !tid) return;
        modeSelect.value = "relationship";
        selectedMode = "relationship";
        step2Characteristic.classList.add("hidden");
        resultCard.classList.add("hidden");
        resetSelect(sourceSelect, "Выберите первый профиль");
        resetSelect(targetSelect, "Выберите второй профиль");
        const resp = await fetch("/api/options/?mode=relationship");
        const data = await resp.json();
        data.items.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.label;
            sourceSelect.appendChild(opt);
        });
        step2Relationship.classList.remove("hidden");
        sourceSelect.value = sid;
        if (!sourceSelect.value) return;
        const rt = await fetch(`/api/relationship-targets/?source_id=${encodeURIComponent(sid)}`);
        const targets = await rt.json();
        targets.items.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.label;
            targetSelect.appendChild(opt);
        });
        targetSelect.value = tid;
        if (!targetSelect.value) return;
        await showResult(
            `/api/result/?mode=relationship&source_id=${encodeURIComponent(sid)}&target_id=${encodeURIComponent(tid)}`
        );
    }
});
