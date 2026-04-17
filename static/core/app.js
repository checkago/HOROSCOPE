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
