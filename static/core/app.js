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
    if (seo.profile_slug || seo.profile_id != null) {
        u.searchParams.set("mode", "characteristic");
        if (seo.profile_slug) {
            u.searchParams.set("profile", String(seo.profile_slug));
            u.searchParams.delete("profile_id");
        } else {
            u.searchParams.set("profile_id", String(seo.profile_id));
        }
        u.searchParams.delete("source_id");
        u.searchParams.delete("target_id");
        u.searchParams.delete("source");
        u.searchParams.delete("target");
        window.history.replaceState(null, "", `${u.pathname}?${u.searchParams.toString()}`);
        return;
    }
    if (seo.source_slug && seo.target_slug) {
        u.searchParams.set("mode", "relationship");
        u.searchParams.set("source", String(seo.source_slug));
        u.searchParams.set("target", String(seo.target_slug));
        u.searchParams.delete("profile_id");
        u.searchParams.delete("profile");
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
        u.searchParams.delete("profile");
        u.searchParams.delete("source");
        u.searchParams.delete("target");
        window.history.replaceState(null, "", `${u.pathname}?${u.searchParams.toString()}`);
    }
}

const modeSelect = document.getElementById("mode-select");
const step2Characteristic = document.getElementById("step-2-characteristic");
const step2Relationship = document.getElementById("step-2-relationship");
const step2Daily = document.getElementById("step-2-daily");
const profileSelect = document.getElementById("profile-select");
const sourceSelect = document.getElementById("source-select");
const targetSelect = document.getElementById("target-select");
const dailyProfileSelect = document.getElementById("daily-profile-select");
const showCharacteristicBtn = document.getElementById("show-characteristic-btn");
const showRelationshipBtn = document.getElementById("show-relationship-btn");
const showDailyBtn = document.getElementById("show-daily-btn");
const resultCard = document.getElementById("result-card");
const resultTitle = document.getElementById("result-title");
const resultContent = document.getElementById("result-content");
const backToTopMainBtn = document.getElementById("back-to-top-main");

let selectedMode = "";

const updateBackToTopMainVisibility = () => {
    if (!backToTopMainBtn || !resultCard || !resultContent) return;
    const hasLongResult = (resultContent.textContent || "").trim().length > 700;
    const canShow = !resultCard.classList.contains("hidden") && hasLongResult && window.scrollY > 420;
    backToTopMainBtn.classList.toggle("is-visible", canShow);
};

const resetSelect = (el, text) => {
    el.innerHTML = `<option value="">${text}</option>`;
};

modeSelect.addEventListener("change", async (e) => {
    selectedMode = e.target.value;
    resetSeoToDefaults();
    resultCard.classList.add("hidden");
    updateBackToTopMainVisibility();
    resetSelect(profileSelect, "Выберите профиль");
    resetSelect(sourceSelect, "Выберите первый профиль");
    resetSelect(targetSelect, "Сначала выберите профиль 1");
    resetSelect(dailyProfileSelect, "Выберите профиль");

    step2Characteristic.classList.add("hidden");
    step2Relationship.classList.add("hidden");
    step2Daily.classList.add("hidden");

    if (!selectedMode) return;

    const resp = await fetch(`/api/options/?mode=${selectedMode}`);
    const data = await resp.json();

    if (selectedMode === "characteristic" || selectedMode === "daily") {
        const targetSelectEl = selectedMode === "daily" ? dailyProfileSelect : profileSelect;
        data.items.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = item.id;
            if (item.slug) opt.dataset.slug = item.slug;
            opt.textContent = item.label;
            targetSelectEl.appendChild(opt);
        });
        if (selectedMode === "daily") {
            step2Daily.classList.remove("hidden");
        } else {
            step2Characteristic.classList.remove("hidden");
        }
        return;
    }

    data.items.forEach((item) => {
        const opt = document.createElement("option");
        opt.value = item.id;
        if (item.slug) opt.dataset.slug = item.slug;
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
        if (item.slug) opt.dataset.slug = item.slug;
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
    updateBackToTopMainVisibility();
};

const characteristicResultUrl = () => {
    const opt = profileSelect.selectedOptions[0];
    const slug = opt && opt.dataset && opt.dataset.slug;
    if (slug) {
        return `/api/result/?mode=characteristic&profile=${encodeURIComponent(slug)}`;
    }
    return `/api/result/?mode=characteristic&profile_id=${encodeURIComponent(profileSelect.value)}`;
};

const relationshipResultUrl = () => {
    const so = sourceSelect.selectedOptions[0];
    const to = targetSelect.selectedOptions[0];
    const ss = so && so.dataset && so.dataset.slug;
    const ts = to && to.dataset && to.dataset.slug;
    if (ss && ts) {
        return `/api/result/?mode=relationship&source=${encodeURIComponent(ss)}&target=${encodeURIComponent(ts)}`;
    }
    return `/api/result/?mode=relationship&source_id=${encodeURIComponent(sourceSelect.value)}&target_id=${encodeURIComponent(targetSelect.value)}`;
};

const dailyResultUrl = () => {
    const opt = dailyProfileSelect.selectedOptions[0];
    const slug = opt && opt.dataset && opt.dataset.slug;
    if (slug) {
        return `/api/result/?mode=daily&profile=${encodeURIComponent(slug)}`;
    }
    return `/api/result/?mode=daily&profile_id=${encodeURIComponent(dailyProfileSelect.value)}`;
};

showCharacteristicBtn.addEventListener("click", async () => {
    if (!profileSelect.value) return;
    await showResult(characteristicResultUrl());
});

showRelationshipBtn.addEventListener("click", async () => {
    if (!sourceSelect.value || !targetSelect.value) return;
    await showResult(relationshipResultUrl());
});

showDailyBtn.addEventListener("click", async () => {
    if (!dailyProfileSelect.value) return;
    await showResult(dailyResultUrl());
});

const readSsrState = () => {
    const el = document.getElementById("ssr-state");
    if (!el || !el.textContent) return null;
    try {
        return JSON.parse(el.textContent);
    } catch {
        return null;
    }
};

document.addEventListener("DOMContentLoaded", async () => {
    if (backToTopMainBtn) {
        backToTopMainBtn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
        window.addEventListener("scroll", updateBackToTopMainVisibility, { passive: true });
    }

    const p = new URLSearchParams(window.location.search);
    const mode = p.get("mode");
    const ssr = readSsrState();

    if (mode === "characteristic") {
        const want = p.get("profile") || p.get("profile_id");
        if (!want) return;
        modeSelect.value = "characteristic";
        selectedMode = "characteristic";
        step2Relationship.classList.add("hidden");
        if (!ssr || !ssr.skip_initial_result_fetch) {
            resultCard.classList.add("hidden");
        }
        resetSelect(profileSelect, "Выберите профиль");
        const resp = await fetch("/api/options/?mode=characteristic");
        const data = await resp.json();
        data.items.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = item.id;
            if (item.slug) opt.dataset.slug = item.slug;
            opt.textContent = item.label;
            profileSelect.appendChild(opt);
        });
        step2Characteristic.classList.remove("hidden");
        const found = data.items.find(
            (it) => String(it.id) === want || (it.slug && it.slug === want)
        );
        if (!found) return;
        profileSelect.value = String(found.id);
        if (!profileSelect.value) return;
        if (ssr && ssr.skip_initial_result_fetch && ssr.mode === "characteristic") {
            if (ssr.seo) applyDynamicSeo(ssr.seo);
            resultTitle.textContent = ssr.title || "";
            resultContent.classList.remove("relationship-view");
            resultContent.classList.add("characteristic-view");
            updateBackToTopMainVisibility();
            return;
        }
        const isNumeric = /^\d+$/.test(String(want));
        const url = isNumeric
            ? `/api/result/?mode=characteristic&profile_id=${encodeURIComponent(want)}`
            : `/api/result/?mode=characteristic&profile=${encodeURIComponent(want)}`;
        await showResult(url);
        return;
    }

    if (mode === "relationship") {
        const sid = p.get("source") || p.get("source_id");
        const tid = p.get("target") || p.get("target_id");
        if (!sid || !tid) return;
        modeSelect.value = "relationship";
        selectedMode = "relationship";
        step2Characteristic.classList.add("hidden");
        if (!ssr || !ssr.skip_initial_result_fetch) {
            resultCard.classList.add("hidden");
        }
        resetSelect(sourceSelect, "Выберите первый профиль");
        resetSelect(targetSelect, "Выберите второй профиль");
        const resp = await fetch("/api/options/?mode=relationship");
        const data = await resp.json();
        data.items.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = item.id;
            if (item.slug) opt.dataset.slug = item.slug;
            opt.textContent = item.label;
            sourceSelect.appendChild(opt);
        });
        step2Relationship.classList.remove("hidden");
        const srcFound = data.items.find(
            (it) => String(it.id) === sid || (it.slug && it.slug === sid)
        );
        if (!srcFound) return;
        sourceSelect.value = String(srcFound.id);
        if (!sourceSelect.value) return;
        const rt = await fetch(`/api/relationship-targets/?source_id=${encodeURIComponent(sourceSelect.value)}`);
        const targets = await rt.json();
        targets.items.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = item.id;
            if (item.slug) opt.dataset.slug = item.slug;
            opt.textContent = item.label;
            targetSelect.appendChild(opt);
        });
        const tgtFound = targets.items.find(
            (it) => String(it.id) === tid || (it.slug && it.slug === tid)
        );
        if (!tgtFound) return;
        targetSelect.value = String(tgtFound.id);
        if (!targetSelect.value) return;
        if (ssr && ssr.skip_initial_result_fetch && ssr.mode === "relationship") {
            if (ssr.seo) applyDynamicSeo(ssr.seo);
            resultTitle.textContent = ssr.title || "";
            resultContent.classList.remove("characteristic-view");
            resultContent.classList.add("relationship-view");
            stylizeRelationshipMarkup();
            updateBackToTopMainVisibility();
            return;
        }
        const sidNum = /^\d+$/.test(String(sid));
        const tidNum = /^\d+$/.test(String(tid));
        const url =
            sidNum && tidNum
                ? `/api/result/?mode=relationship&source_id=${encodeURIComponent(sid)}&target_id=${encodeURIComponent(tid)}`
                : `/api/result/?mode=relationship&source=${encodeURIComponent(sid)}&target=${encodeURIComponent(tid)}`;
        await showResult(url);
        return;
    }

    if (mode === "daily") {
        const want = p.get("profile") || p.get("profile_id");
        if (!want) return;
        modeSelect.value = "daily";
        selectedMode = "daily";
        step2Characteristic.classList.add("hidden");
        step2Relationship.classList.add("hidden");
        if (!ssr || !ssr.skip_initial_result_fetch) {
            resultCard.classList.add("hidden");
        }
        resetSelect(dailyProfileSelect, "Выберите профиль");
        const resp = await fetch("/api/options/?mode=daily");
        const data = await resp.json();
        data.items.forEach((item) => {
            const opt = document.createElement("option");
            opt.value = item.id;
            if (item.slug) opt.dataset.slug = item.slug;
            opt.textContent = item.label;
            dailyProfileSelect.appendChild(opt);
        });
        step2Daily.classList.remove("hidden");
        const found = data.items.find(
            (it) => String(it.id) === want || (it.slug && it.slug === want)
        );
        if (!found) return;
        dailyProfileSelect.value = String(found.id);
        if (!dailyProfileSelect.value) return;
        const isNumeric = /^\d+$/.test(String(want));
        const url = isNumeric
            ? `/api/result/?mode=daily&profile_id=${encodeURIComponent(want)}`
            : `/api/result/?mode=daily&profile=${encodeURIComponent(want)}`;
        await showResult(url);
    }

    updateBackToTopMainVisibility();
});
