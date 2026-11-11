"""Load a saved phishing model and predict whether an email looks legitimate."""

from __future__ import annotations

from pathlib import Path
import time
from typing import Any

import joblib

try:
    from .data_preparation import LABEL_MAPPING  # type: ignore
except ImportError:  # pragma: no cover - fallback for direct script execution
    from data_preparation import LABEL_MAPPING  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "email_model.joblib"
_MODEL_CACHE: dict[str, Any] = {}

LABEL_NAME_MAP = {
    0: "legitimate",
    1: "phishing",
}


def get_default_model_path() -> Path:
    """Return the trained model path, independent of the current working directory."""
    return DEFAULT_MODEL_PATH


def combine_email_text(subject: str, body: str) -> str:
    """Format the email text in the same way used during model training."""
    subject_text = "" if subject is None else str(subject).strip()
    body_text = "" if body is None else str(body).strip()
    return f"{subject_text} {body_text}".strip()


def validate_email_input(subject: str, body: str) -> str:
    """Check that there is usable email text and return the combined text."""
    if subject is None and body is None:
        raise ValueError("Email subject and body cannot both be empty.")

    if not isinstance(subject, str) or not isinstance(body, str):
        raise TypeError("Email subject and body must be strings.")

    combined = combine_email_text(subject, body)
    if not combined:
        raise ValueError("Email subject and body cannot be empty after trimming whitespace.")

    return combined


def load_model(model_path: str | Path | None = None) -> Any:
    """Load the saved model without retraining it and cache it in memory."""
    model_file = Path(model_path) if model_path is not None else get_default_model_path()
    model_file = model_file.resolve()
    model_directory = (PROJECT_ROOT / "models").resolve()
    if model_file.parent != model_directory or model_file.suffix != ".joblib":
        raise ValueError("Model files must be trusted .joblib files in the models directory.")
    model_key = str(model_file.resolve())

    if model_key in _MODEL_CACHE:
        return _MODEL_CACHE[model_key]

    if not model_file.exists():
        raise FileNotFoundError(
            f"Model file not found at '{model_file}'. "
            "Train the model first with: python src/train_email_model.py"
        )

    start = time.perf_counter()
    model = joblib.load(model_file)
    elapsed = time.perf_counter() - start
    print(f"[timing] Loaded model from disk in {elapsed:.3f}s: {model_file}")
    _MODEL_CACHE[model_key] = model
    return model


def predict_email(
    subject: str,
    body: str,
    model_path: str | Path | None = None,
    model: Any | None = None,
) -> dict[str, Any]:
    """Classify an email and return a simple, readable result."""
    combined_text = validate_email_input(subject, body)
    model_instance = model if model is not None else load_model(model_path)

    if not hasattr(model_instance, "predict"):
        raise TypeError("The loaded model does not support prediction.")

    start = time.perf_counter()
    prediction = model_instance.predict([combined_text])[0]
    elapsed = time.perf_counter() - start
    print(f"[timing] Prediction took {elapsed:.4f}s for one email.")

    label = int(prediction)
    prediction_name = LABEL_NAME_MAP.get(label, str(label))

    response: dict[str, Any] = {
        "prediction": prediction_name.title(),
        "label": label,
        "probabilities": None,
    }

    if hasattr(model_instance, "predict_proba"):
        probabilities = model_instance.predict_proba([combined_text])[0]
        mapped_probabilities: dict[str, float] = {}

        for class_value, probability in zip(model_instance.classes_, probabilities):
            class_key = LABEL_NAME_MAP.get(int(class_value), str(class_value))
            mapped_probabilities[class_key] = float(probability)

        response["probabilities"] = mapped_probabilities

    return response
