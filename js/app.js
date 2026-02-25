const form = document.getElementById("studyForm");
const searchBtn = document.getElementById("searchBtn");
const loadingEl = document.getElementById("loading");
const resultsEl = document.getElementById("results");
const errorEl = document.getElementById("error");

const sections = {
    literature: document.getElementById("literatureContent"),
    pk: document.getElementById("pkContent"),
    design: document.getElementById("designContent"),
    sample: document.getElementById("sampleSizeContent"),
    regulatory: document.getElementById("regulatoryContent"),
};

function setLoading(isLoading) {
    loadingEl.style.display = isLoading ? "grid" : "none";
}

function clearError() {
    errorEl.style.display = "none";
    errorEl.textContent = "";
}

function showError(message) {
    errorEl.textContent = message;
    errorEl.style.display = "block";
    resultsEl.style.display = "none";
}

function safe(value, fallback = "—") {
    if (value === null || value === undefined || value === "") {
        return fallback;
    }
    return value;
}

function getPayload() {
    const data = new FormData(form);
    const cvintraRaw = data.get("cvintra");
    const cvintra = cvintraRaw ? Number(cvintraRaw) : null;

    return {
        inn: data.get("inn"),
        dosage_form: data.get("dosageForm"),
        dosage: data.get("dosage"),
        administration_mode: data.get("administrationMode"),
        cvintra: Number.isFinite(cvintra) ? cvintra : null,
        output_format: data.get("outputFormat"),
    };
}

function renderAnalysis(data) {
    const pubmed = data?.literature?.pubmed;
    const pk = data?.pk_parameters;
    const design = data?.design_recommendation;
    const sample = data?.sample_size;
    const regs = data?.regulatory_check;

    sections.literature.innerHTML = `
        <p><strong>PubMed статей:</strong> ${safe(pubmed?.count, 0)}</p>
        <p><a href="${safe(pubmed?.search_url, "#")}" target="_blank" rel="noopener noreferrer">Открыть поиск в PubMed</a></p>
    `;

    sections.pk.innerHTML = `
        <p><strong>Cmax:</strong> ${safe(pk?.cmax?.value)}</p>
        <p><strong>AUC:</strong> ${safe(pk?.auc?.value)}</p>
        <p><strong>CVintra:</strong> ${safe(pk?.cvintra?.value)}</p>
    `;

    sections.design.innerHTML = `
        <p><strong>Рекомендованный дизайн:</strong> ${safe(design?.recommended_design)}</p>
        <p><strong>Обоснование:</strong> ${safe(design?.rationale)}</p>
    `;

    sections.sample.innerHTML = `
        <p><strong>Базовый размер:</strong> ${safe(sample?.base_sample_size)}</p>
        <p><strong>С учетом выбывания:</strong> ${safe(sample?.final_sample_size)}</p>
    `;

    const regItems = regs
        ? Object.entries(regs)
            .map(([name, value]) => `<li><strong>${name.toUpperCase()}</strong>: ${value?.compliant ? "соответствует" : "не соответствует"}</li>`)
            .join("")
        : "<li>Нет данных</li>";
    sections.regulatory.innerHTML = `<ul>${regItems}</ul>`;

    resultsEl.style.display = "block";
}

async function requestAnalysis() {
    clearError();
    setLoading(true);

    try {
        const payload = getPayload();
        if (!payload.inn) {
            throw new Error("Введите МНН препарата");
        }

        const response = await fetch("/api/full-analysis", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.error || "Ошибка запроса к API");
        }

        const result = await response.json();
        renderAnalysis(result);
    } catch (error) {
        showError(error.message || "Непредвиденная ошибка");
    } finally {
        setLoading(false);
    }
}

searchBtn.addEventListener("click", requestAnalysis);

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    await requestAnalysis();
});
