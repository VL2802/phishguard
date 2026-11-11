# PhishGuard

PhishGuard is a machine-learning prototype that classifies email text as
legitimate or potentially phishing. It combines a scikit-learn TF-IDF and
Logistic Regression pipeline with a small FastAPI service and a browser
extension interface.

This project is intended for learning and experimentation. It is not a
production anti-phishing system and must not be used as the sole basis for
security decisions.

## Features

- Prepare labelled email datasets with validation and duplicate removal.
- Train and evaluate a binary text-classification pipeline.
- Save and reuse a trained model locally.
- Validate API input for email subject and body.
- Expose health and email-analysis endpoints through FastAPI.
- Display analysis results in the PhishGuard browser-extension prototype.

## Technology

- Python 3.11+ recommended
- pandas
- scikit-learn
- joblib
- FastAPI and Uvicorn
- pytest
- Vanilla JavaScript, HTML, and CSS for the extension

## Architecture

The training scripts read a local CSV dataset and produce a serialized
scikit-learn pipeline under `models/`. The FastAPI application loads that model
once at startup and serves predictions at `/api/analyze-email`. The browser
extension sends local requests to the API and renders the response.

```text
phishing-detection/
├── src/                    # Data preparation, training, prediction, API
├── tests/                  # Unit tests for prediction behavior
├── phishguard-extension/   # Current browser-extension prototype
├── first-extension/        # Earlier extension prototype
├── data/                   # Local datasets; excluded from Git
├── models/                 # Generated model artifacts; excluded from Git
├── requirements.txt
├── README.md
└── SECURITY.md
```

## Dataset and model files

The local workspace contains AURA email datasets and a generated model. Raw
email datasets may contain personal or copyrighted content, so they are excluded
from this repository. Obtain an appropriately licensed dataset separately and
place it at `data/aura/Nazario_5.csv`, with `subject`, `body`, and `label`
columns. The expected labels are `1` for phishing and `0` for legitimate.

The generated `models/email_model.joblib` file is also excluded. Train it
locally before starting the API.

## Setup

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Train the model

After placing an approved dataset at the documented path:

```powershell
.\.venv\Scripts\python.exe src\train_email_model.py
```

The script reports accuracy, precision, recall, F1-score, and a confusion
matrix, then writes `models/email_model.joblib`.

## Run the API

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api:app --reload --host 127.0.0.1 --port 8000
```

Endpoints:

- `GET http://127.0.0.1:8000/health`
- `POST http://127.0.0.1:8000/api/analyze-email`

Example request:

```json
{
  "subject": "Urgent: Verify your account",
  "body": "Your account will be suspended. Enter your password."
}
```

## Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The tests use mocked models and do not require the excluded dataset or trained
model artifact.

## Browser extension

Load `phishguard-extension/` as an unpacked extension in a Chromium-based browser
after starting the API. The extension currently uses the local API URL
`http://127.0.0.1:8000`. Its interface is a prototype and does not yet inspect
messages directly from a mail client.

## Screenshots

Screenshots can be added here after the API and extension are run together.

## Future improvements

- Evaluate against multiple licensed datasets and a held-out test set.
- Add authentication and rate limiting before exposing the API beyond localhost.
- Bundle local fonts/icons if a specific visual typeface is required.
- Add model versioning, reproducible experiment metadata, and CI checks.
- Add calibrated confidence guidance and a human-review workflow.
