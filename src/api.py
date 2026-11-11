"""Minimal FastAPI layer for phishing detection."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

try:
    from .email_predictor import load_model, predict_email
except ImportError:  # pragma: no cover - direct script execution fallback
    from email_predictor import load_model, predict_email

app = FastAPI(title="PhishGuard API")


@app.on_event("startup")
def startup_event() -> None:
    """Load the saved model once at API startup instead of per request."""
    app.state.model = load_model()

# Restrict CORS to the local frontend origin currently used for development.
# Inspect the extension and browser dev server configuration before broadening this.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^chrome-extension://.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmailRequest(BaseModel):
    subject: str = Field(..., min_length=1, description="Email subject")
    body: str = Field(..., min_length=1, description="Email body")

    @field_validator("subject", "body")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if value is None:
            raise ValueError("Email text cannot be null.")
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Email text cannot be empty.")
        return value


@app.get("/health")
def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok"}


@app.post("/api/analyze-email")
def analyze_email(request: EmailRequest) -> dict[str, Any]:
    """Analyze an email and return the predicted phishing result."""
    try:
        result = predict_email(request.subject, request.body, model=app.state.model)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Model is not available. Train the model first or check the model path.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive error handling
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc

    return {
        "prediction": result["prediction"],
        "label": result["label"],
        "probabilities": result.get("probabilities"),
    }
