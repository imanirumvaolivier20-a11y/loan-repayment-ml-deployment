document.addEventListener("DOMContentLoaded", () => {

    const singleForm = document.getElementById("singleForm");
    const singleResult = document.getElementById("singleResult");
    const csvInput = document.getElementById("csvInput");
    const csvBtn = document.getElementById("csvPredictBtn");

    const csvTable = document.getElementById("csvTable");
    const logsTable = document.getElementById("logsTable");

    /* ================= SINGLE ================= */
    singleForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const payload = Object.fromEntries(new FormData(singleForm).entries());
        Object.keys(payload).forEach(k => {
            if (!isNaN(payload[k])) payload[k] = parseFloat(payload[k]);
        });

        const res = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        const isGood = data.prediction === "Will pay back";

        singleResult.className = "result-box " + (isGood ? "success" : "danger");
        singleResult.innerHTML = `
            <h3>${data.prediction}</h3>
            <p>Pay back: ${(data.probability_paid_back * 100).toFixed(2)}%</p>
            <p>Not pay back: ${(data.probability_not_paid_back * 100).toFixed(2)}%</p>
        `;
    });

    /* ================= CSV ================= */
    csvBtn.addEventListener("click", async () => {
        if (!csvInput.files.length) return alert("Upload CSV");

        const fd = new FormData();
        fd.append("file", csvInput.files[0]);

        const res = await fetch("/predict_csv", { method: "POST", body: fd });
        const data = await res.json();

        renderTable(csvTable, data);
    });
    /* ================= LOGS ================= */
    window.loadLogs = async () => {
    try {
        const res = await fetch("/logs");
        const data = await res.json();
        renderTable(logsTable, data);
    } catch (err) {
        console.error("Failed to load logs:", err);
        logsTable.innerHTML = "<tr><td>Error loading logs</td></tr>";
    }
};

    /* ================= TABLE ================= */
    function renderTable(table, data) {
        if (!data.length) {
            table.innerHTML = "<tr><td>No data</td></tr>";
            return;
        }

        const cols = [
            "prediction",
            "probability_paid_back",
            "probability_not_paid_back",
            "credit_score",
            "loan_amount"
        ];

        let html = "<tr>";
        cols.forEach(c => html += `<th>${c.replace(/_/g," ")}</th>`);
        html += "</tr>";

        data.forEach(row => {
            html += "<tr>";
            cols.forEach(c => {
                let v = row[c];
                if (c.includes("probability")) v = (v * 100).toFixed(2) + "%";
                html += `<td>${v ?? "-"}</td>`;
            });
            html += "</tr>";
        });

        table.innerHTML = html;
    }

});
