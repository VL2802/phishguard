"""Prepare the AURA email dataset for phishing detection.

This module keeps the preprocessing simple and easy to explain. It reads the CSV,
checks the required columns, cleans missing values, combines subject and body,
and prepares a binary label column.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

REQUIRED_COLUMNS = ["subject", "body", "label"]

# The dataset examples in Nazario_5.csv show that label 1 corresponds to phishing
# or suspicious messages, while label 0 corresponds to legitimate messages.
# This mapping remains configurable here so the project can be adapted if a new
# dataset uses a different convention.
LABEL_MAPPING = {
    "phishing": 1,
    "legitimate": 0,
}


def project_root() -> Path:
    """Return the project root directory regardless of the working directory."""
    return Path(__file__).resolve().parent.parent


def dataset_path() -> Path:
    """Return the default dataset path used by the project."""
    return project_root() / "data" / "aura" / "Nazario_5.csv"


def validate_required_columns(df: pd.DataFrame) -> None:
    """Raise a clear error if required email columns are missing."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(missing_columns)
        )


def normalize_labels(series: pd.Series) -> pd.Series:
    """Convert labels to a strict binary integer format.

    The AURA dataset uses 0 and 1, but the function keeps the conversion explicit
    and fails early if the dataset uses unexpected label values.
    """
    converted = pd.to_numeric(series, errors="coerce")
    valid_unique = sorted(converted.dropna().unique().tolist())

    if not valid_unique:
        raise ValueError("No valid labels were found in the dataset.")

    if set(valid_unique) != {0, 1}:
        raise ValueError(
            "Expected binary labels 0 and 1 only. "
            f"Found labels: {valid_unique}."
        )

    return converted.astype(int)


def prepare_dataset(
    dataset_file: Optional[str | Path] = None,
    *,
    show_summary: bool = True,
) -> pd.DataFrame:
    """Load and clean the email dataset.

    Steps kept deliberately simple:
    - load the CSV.
    - check required columns.
    - show dataset overview.
    - remove rows with missing labels.
    - replace missing text with empty strings.
    - combine subject and body into one text field.
    - remove exact duplicates before the train/test split.
    - verify both classes are present.
    """
    data_path = Path(dataset_file) if dataset_file is not None else dataset_path()
    df = pd.read_csv(data_path, low_memory=False)

    validate_required_columns(df)

    if show_summary:
        print(f"Dataset shape: {df.shape}")
        print("Columns:", list(df.columns))
        print("\nMissing values:")
        print(df[REQUIRED_COLUMNS].isnull().sum().to_string())
        print("\nLabel distribution before cleaning:")
        print(df["label"].value_counts(dropna=False).to_string())

    df = df.copy()
    df = df.dropna(subset=["label"]).copy()

    for column in ["subject", "body"]:
        df[column] = df[column].fillna("").astype(str)

    df["subject"] = df["subject"].str.strip()
    df["body"] = df["body"].str.strip()

    df["combined_text"] = (
        df["subject"].fillna("").astype(str)
        + " "
        + df["body"].fillna("").astype(str)
    ).str.strip()

    # Remove exact duplicates before training to avoid leakage.
    original_rows = len(df)
    df = df.drop_duplicates(subset=["subject", "body", "label"], keep="first").copy()
    removed_duplicates = original_rows - len(df)
    if removed_duplicates > 0 and show_summary:
        print(f"\nRemoved {removed_duplicates} duplicate rows before splitting.")

    df["label"] = normalize_labels(df["label"])

    if df["label"].nunique() < 2:
        raise ValueError(
            "The cleaned dataset must contain both phishing and legitimate emails. "
            f"Found labels: {sorted(df['label'].unique().tolist())}"
        )

    if show_summary:
        print("\nCleaned dataset summary:")
        print(f"Rows after cleaning: {len(df):,}")
        print(f"Columns: {list(df.columns)}")
        print("\nLabel distribution after cleaning:")
        print(df["label"].value_counts().sort_index().to_string())
        print("\nSample rows:")
        print(df[["subject", "body", "label"]].head(3).to_string(index=False, max_colwidth=120))

    return df
