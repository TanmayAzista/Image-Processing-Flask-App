// opsUI.js
// Handles transformation UI and interaction with backend

const OpsUI = (function () {
    let opsConfig = null;

    let categorySelect = null;
    let operationSelect = null;
    let paramsContainer = null;
    let applyButton = null;

    async function init() {
        categorySelect = document.getElementById("op-category");
        operationSelect = document.getElementById("op-operation");
        paramsContainer = document.getElementById("op-params");
        applyButton = document.getElementById("op-apply");

        if (!categorySelect || !operationSelect || !paramsContainer || !applyButton) {
            console.warn("OpsUI: required DOM elements missing");
            return;
        }

        await loadConfig();
        populateCategories();
        attachHandlers();
    }

    async function loadConfig() {
        const res = await fetch("/static/ops_config.jsonc");
        opsConfig = await res.json();
        console.log("Loaded Config", opsConfig)
    }

    function populateCategories() {
        categorySelect.innerHTML = "";

        Object.entries(opsConfig.categories).forEach(([key, cat]) => {
            const opt = document.createElement("option");
            opt.value = key;
            opt.textContent = cat.label;
            categorySelect.appendChild(opt);
        });

        populateOperations(categorySelect.value);
    }

    function populateOperations(categoryKey) {
        operationSelect.innerHTML = "";
        paramsContainer.innerHTML = "";

        const ops = opsConfig.categories[categoryKey].operations;

        Object.entries(ops).forEach(([key, op]) => {
            const opt = document.createElement("option");
            opt.value = key;
            opt.textContent = op.label;
            operationSelect.appendChild(opt);
        });

        renderParams(categoryKey, operationSelect.value);
    }

    function renderParams(categoryKey, operationKey) {
        paramsContainer.innerHTML = "";

        const params =
            opsConfig.categories[categoryKey].operations[operationKey].params;

        Object.entries(params).forEach(([name, meta]) => {
            const wrapper = document.createElement("div");
            wrapper.className = "param-row";

            const label = document.createElement("label");
            label.textContent = name;

            const input = document.createElement("input");
            input.type = meta.type;
            input.value = meta.default;
            input.step = meta.step ?? "any";
            if (meta.min !== undefined) input.min = meta.min;
            if (meta.max !== undefined) input.max = meta.max;

            input.dataset.paramName = name;

            wrapper.appendChild(label);
            wrapper.appendChild(input);
            paramsContainer.appendChild(wrapper);
        });
    }

    function collectParams() {
        const params = {};
        paramsContainer.querySelectorAll("input").forEach(input => {
            params[input.dataset.paramName] = Number(input.value);
        });
        return params;
    }

    async function applyTransform() {
        const category = categorySelect.value;
        const operation = operationSelect.value;
        const params = collectParams();

        const res = await fetch("/transform", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                op: operation,
                params: params
            })
        });

        if (!res.ok) {
            alert("Transformation failed");
            return;
        }
        await fetchStackState();
        // Re-render current image
        ImageViewer.reload();
    }

    function attachHandlers() {
        categorySelect.addEventListener("change", () => {
            populateOperations(categorySelect.value);
        });

        operationSelect.addEventListener("change", () => {
            renderParams(categorySelect.value, operationSelect.value);
        });

        applyButton.addEventListener("click", applyTransform);
    }

    return {
        init
    };
})();
