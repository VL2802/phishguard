"""Train a TF-IDF + Logistic Regression model for phishing detection."""

from __future__ import annotations

from pathlib import Path
import time

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

try:
    from .data_preparation import prepare_dataset
except ImportError:  # pragma: no cover - direct script execution
    from data_preparation import prepare_dataset


CLASS_LABELS = [0, 1]
CLASS_NAMES = ["legitimate", "phishing"]


def build_model() -> Pipeline:
    """Create a simple text classification pipeline."""
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    max_features=30000,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    dataset_path = project_root / "data" / "aura" / "Nazario_5.csv"
    model_path = project_root / "models" / "email_model.joblib"

    print("Loading and preparing the dataset...")
    start = time.perf_counter()
    df = prepare_dataset(dataset_path)
    elapsed = time.perf_counter() - start
    print(f"[timing] Data loading and preprocessing took {elapsed:.3f}s")

    X = df["combined_text"]
    y = df["label"].astype(int)

    start = time.perf_counter()
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )
    print(f"[timing] Train/test split took {time.perf_counter() - start:.3f}s")

    print("\nTraining the TF-IDF + Logistic Regression model...")
    start = time.perf_counter()
    model = build_model()
    model.fit(X_train, y_train)
    print(f"[timing] Model training took {time.perf_counter() - start:.3f}s")

    start = time.perf_counter()
    predictions = model.predict(X_test)
    print(f"[timing] Model evaluation (prediction) took {time.perf_counter() - start:.3f}s")

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, pos_label=1, zero_division=0)
    recall = recall_score(y_test, predictions, pos_label=1, zero_division=0)
    f1 = f1_score(y_test, predictions, pos_label=1, zero_division=0)

    print("\n" + "=" * 60)
    print("MODEL EVALUATION RESULTS")
    print("=" * 60)
    print("Positive class: phishing (label 1)")
    print(f"Accuracy : {accuracy:.4f} ({accuracy:.2%})")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=CLASS_LABELS,
            target_names=CLASS_NAMES,
            digits=4,
            zero_division=0,
        )
    )

    matrix = confusion_matrix(y_test, predictions, labels=CLASS_LABELS)
    tn, fp, fn, tp = matrix.ravel()
    print("Confusion matrix (rows = actual, columns = predicted):")
    print("                    Predicted legitimate  Predicted phishing")
    print(f"Actual legitimate            {tn:>6}             {fp:>6}")
    print(f"Actual phishing              {fn:>6}             {tp:>6}")
    print("\nConfusion matrix guide:")
    print(f"- True negative (TN): {tn} legitimate emails correctly identified as legitimate.")
    print(f"- False positive (FP): {fp} legitimate emails incorrectly flagged as phishing.")
    print(f"- False negative (FN): {fn} phishing emails incorrectly marked as legitimate.")
    print(f"- True positive (TP): {tp} phishing emails correctly identified as phishing.")

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")

    print("\nExample prediction:")
    example_email = (
        "Urgent: Verify your account immediately to avoid suspension. "
        "Enter your password and confirm your identity."
    )
    predicted_label = model.predict([example_email])[0]
    print(f"Predicted label: {predicted_label}")
    print("Classes used by the model:", model.classes_)
    if hasattr(model, "predict_proba"):
        print("Probability distribution:", model.predict_proba([example_email])[0])


if __name__ == "__main__":
    main()
