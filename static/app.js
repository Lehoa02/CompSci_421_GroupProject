let features = [];

// --- helpers / classifiers ---

function classifyBrightness(centroid) {
    if (centroid < 2000) return { label: "Dark", cls: "tag-dark" };
    if (centroid < 3500) return { label: "Neutral", cls: "tag-neutral" };
    return { label: "Bright", cls: "tag-bright" };
}

function classifyComplexity(bandwidth) {
    if (bandwidth < 2500) return { label: "Simple", cls: "tag-simple" };
    return { label: "Complex", cls: "tag-complex" };
}

function classifyLoudness(rms) {
    if (rms < 0.05) return { label: "Quiet", cls: "tag-quiet" };
    return { label: "Loud", cls: "tag-loud" };
}

function normalize(value, min, max) {
    if (max === min) return 0.4;
    const t = (value - min) / (max - min);
    return 0.2 + 0.8 * Math.min(Math.max(t, 0), 1); // keep between 0.2–1 for nicer visuals
}

// --- rendering ---

function renderCards(data) {
    const grid = document.getElementById("grid");
    const empty = document.getElementById("empty-state");
    const count = document.getElementById("file-count");

    grid.innerHTML = "";

    if (!data.length) {
        empty.style.display = "block";
        count.textContent = "0 files";
        return;
    }
    empty.style.display = "none";
    count.textContent = `${data.length} file${data.length === 1 ? "" : "s"}`;

    const centroidVals = data.map(d => d.spectral_centroid_mean);
    const bwVals = data.map(d => d.spectral_bandwidth_mean);
    const rmsVals = data.map(d => d.rms_mean);

    const cMin = Math.min(...centroidVals), cMax = Math.max(...centroidVals);
    const bMin = Math.min(...bwVals), bMax = Math.max(...bwVals);
    const rMin = Math.min(...rmsVals), rMax = Math.max(...rmsVals);

    data.forEach(row => {
        const fileName = row.file_path.split("/").slice(-1)[0];

        const brightness = classifyBrightness(row.spectral_centroid_mean);
        const complexity = classifyComplexity(row.spectral_bandwidth_mean);
        const loudness = classifyLoudness(row.rms_mean);

        const card = document.createElement("div");
        card.className = "card";

        const brightnessFill = normalize(row.spectral_centroid_mean, cMin, cMax);
        const bwFill = normalize(row.spectral_bandwidth_mean, bMin, bMax);
        const rmsFill = normalize(row.rms_mean, rMin, rMax);

        card.innerHTML = `
            <div class="card-header">
                <div>
                    <div class="file-name">${fileName}</div>
                    <div class="sample-rate">${row.sr} Hz</div>
                </div>
            </div>

            <div class="tag-row">
                <span class="tag ${brightness.cls}"><span class="dot"></span>${brightness.label}</span>
                <span class="tag ${complexity.cls}"><span class="dot"></span>${complexity.label}</span>
                <span class="tag ${loudness.cls}"><span class="dot"></span>${loudness.label}</span>
            </div>

            <div class="metric-row">
                <div class="metric">
                    <div class="metric-label">Spectral centroid</div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="transform: scaleX(${brightnessFill});"></div>
                    </div>
                    <div class="metric-value">${row.spectral_centroid_mean.toFixed(0)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Spectral bandwidth</div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="transform: scaleX(${bwFill});"></div>
                    </div>
                    <div class="metric-value">${row.spectral_bandwidth_mean.toFixed(0)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">RMS energy</div>
                    <div class="metric-bar">
                        <div class="metric-fill" style="transform: scaleX(${rmsFill});"></div>
                    </div>
                    <div class="metric-value">${row.rms_mean.toFixed(3)}</div>
                </div>
            </div>
        `;

        grid.appendChild(card);
    });
}

// --- sorting ---

function applySort() {
    const select = document.getElementById("sort-select");
    const value = select.value;
    const sorted = [...features];

    if (value === "brightness-desc") {
        sorted.sort((a, b) => b.spectral_centroid_mean - a.spectral_centroid_mean);
    } else if (value === "brightness-asc") {
        sorted.sort((a, b) => a.spectral_centroid_mean - b.spectral_centroid_mean);
    } else if (value === "loudness-desc") {
        sorted.sort((a, b) => b.rms_mean - a.rms_mean);
    } else if (value === "loudness-asc") {
        sorted.sort((a, b) => a.rms_mean - b.rms_mean);
    }
    renderCards(sorted);
}

document.getElementById("sort-select").addEventListener("change", applySort);

// --- initial load ---

async function loadFeatures() {
    const resp = await fetch("/api/features");
    features = await resp.json();
    renderCards(features);
}

loadFeatures();

// --- upload audio ---

const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const uploadStatus = document.getElementById("upload-status");

uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!fileInput.files.length) {
        uploadStatus.textContent = "Choose a file first.";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    uploadStatus.textContent = "Uploading & analyzing…";

    try {
        const resp = await fetch("/upload", {
            method: "POST",
            body: formData
        });
        const data = await resp.json();

        if (!resp.ok) {
            uploadStatus.textContent = data.error || "Upload failed.";
            return;
        }

        uploadStatus.textContent = "Done ✔";
        fileInput.value = "";

        // add new item to data + re-sort
        features.push(data);
        applySort();
    } catch (err) {
        console.error(err);
        uploadStatus.textContent = "Error during upload.";
    }
});

// --- info panel toggle ---

const infoToggle = document.getElementById("info-toggle");
const infoBody = document.getElementById("info-body");

if (infoToggle && infoBody) {
    infoToggle.addEventListener("click", () => {
        infoBody.classList.toggle("info-body-open");
    });
}
