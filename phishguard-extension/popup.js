const API_BASE_URL = "http://127.0.0.1:8000";

const readyState = document.getElementById("ready-state");
const analyzingState = document.getElementById("analyzing-state");
const resultState = document.getElementById("result-state");

const inspectButton = document.getElementById("inspect-button");
const detailsButton = document.getElementById("details-button");
const resultTitle = document.querySelector("#result-state h2");
const resultText = document.querySelector("#result-state p");
const probabilityCircle = document.querySelector(".probability-circle span");
const riskBadge = document.querySelector(".risk-badge");
const emailDomain = document.querySelector(".domain");

let isRequestInProgress = false;

function showState(state) {
    readyState.classList.add("hidden");
    analyzingState.classList.add("hidden");
    resultState.classList.add("hidden");

    state.classList.remove("hidden");
}

function updateResultUI(payload) {
    const labelName = payload.prediction || "Unknown";
    const probability = payload.probabilities && payload.probabilities.phishing !== undefined
        ? Number(payload.probabilities.phishing) * 100
        : 0;

    if (resultTitle) {
        resultTitle.textContent = labelName === "Phishing" ? "Likely Phishing" : "Likely Legitimate";
    }

    if (resultText) {
        resultText.textContent = labelName === "Phishing"
            ? "The model detected patterns typically associated with phishing emails."
            : "The model did not detect a phishing pattern in this message.";
    }

    if (probabilityCircle) {
        probabilityCircle.textContent = `${Math.round(probability)}%`;
    }

    if (riskBadge) {
        riskBadge.textContent = labelName === "Phishing" ? "High Risk" : "Low Risk";
        riskBadge.style.color = labelName === "Phishing" ? "var(--danger)" : "var(--secondary)";
    }

    if (emailDomain) {
        emailDomain.textContent = "local-api";
    }
}

async function analyzeEmail() {
    if (isRequestInProgress) {
        return;
    }

    isRequestInProgress = true;
    showState(analyzingState);

    const requestBody = {
        subject: "Urgent: Verify your account",
        body: "Your account will be suspended. Enter your password."
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/analyze-email`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || "Backend request failed.");
        }

        const payload = await response.json();
        updateResultUI(payload);
        showState(resultState);
    } catch (error) {
        if (resultTitle) {
            resultTitle.textContent = "Analysis unavailable";
        }

        if (resultText) {
            resultText.textContent = error.message || "Unable to reach the backend API.";
        }

        if (probabilityCircle) {
            probabilityCircle.textContent = "!";
        }

        if (riskBadge) {
            riskBadge.textContent = "Error";
            riskBadge.style.color = "var(--danger)";
        }

        showState(resultState);
    } finally {
        isRequestInProgress = false;
    }
}

inspectButton.addEventListener("click", () => {
    analyzeEmail();
});


detailsButton.addEventListener("click", () => {
    console.log("Details clicked");
});