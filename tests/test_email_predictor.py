from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from src.email_predictor import predict_email


@patch("src.email_predictor.load_model")
def test_predict_email_accepts_subject_and_body(mock_load_model: Mock) -> None:
    model = Mock()
    model.predict.return_value = [1]
    model.predict_proba.return_value = [[0.15, 0.85]]
    model.classes_ = [0, 1]
    mock_load_model.return_value = model

    result = predict_email("Urgent account check", "Verify your password now.", model_path="fake-model.joblib")

    assert result["label"] == 1
    assert result["prediction"] == "Phishing"
    assert result["probabilities"]["legitimate"] == pytest.approx(0.15)
    assert result["probabilities"]["phishing"] == pytest.approx(0.85)


def test_predict_email_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        predict_email("   ", "")


def test_predict_email_handles_missing_model_file() -> None:
    with pytest.raises(FileNotFoundError, match="Model file not found"):
        predict_email("Subject", "Body", model_path="models/missing-model.joblib")


def test_predict_email_rejects_model_outside_trusted_directory() -> None:
    with pytest.raises(ValueError, match="trusted .joblib files"):
        predict_email("Subject", "Body", model_path="untrusted.joblib")


@patch("src.email_predictor.load_model")
def test_predict_email_without_probability_support(mock_load_model: Mock) -> None:
    model = Mock()
    model.predict.return_value = [0]
    del model.predict_proba
    mock_load_model.return_value = model

    result = predict_email("Hello", "Just checking in.", model_path="fake-model.joblib")

    assert result["prediction"] == "Legitimate"
    assert result["label"] == 0
    assert result["probabilities"] is None
