async function makePrediction() {
    const form = document.getElementById("predictionForm");
    const formData = new FormData(form);
    let data = {};

    formData.forEach((value, key) => {
        // send as string; backend casts to float where needed
        data[key] = value;
    });

    const loading = document.getElementById("loading");
    const resultSection = document.getElementById("resultSection");
    const errorMessage = document.getElementById("errorMessage");
    const inputsTableBody = document.querySelector("#inputsTable tbody");

    loading.style.display = "block";
    resultSection.style.display = "none";
    errorMessage.style.display = "none";

    try {
        const response = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        loading.style.display = "none";

        if (response.ok) {
            // Show prediction
            document.getElementById("resultValue").innerText = Number(result.prediction).toFixed(2);

            // Render inputs echo in CSV order
            if (result.inputs && Array.isArray(result.inputs)) {
                inputsTableBody.innerHTML = "";
                result.inputs.forEach((item) => {
                    const tr = document.createElement("tr");
                    const tdName = document.createElement("td");
                    const tdVal = document.createElement("td");
                    tdName.textContent = item.name;
                    tdVal.textContent = item.value;
                    tr.appendChild(tdName);
                    tr.appendChild(tdVal);
                    inputsTableBody.appendChild(tr);
                });
            }

            resultSection.style.display = "block";
        } else {
            errorMessage.innerText = "Prediction failed: " + (result.error || "Unknown error");
            errorMessage.style.display = "block";
        }
    } catch (error) {
        loading.style.display = "none";
        errorMessage.innerText = "Error: " + error.message;
        errorMessage.style.display = "block";
    }
}
