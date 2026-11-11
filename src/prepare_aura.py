
from pathlib import Path
import pandas as pd

data_folder = Path(__file__).parent.parent / "data" / "aura"
file_path = data_folder / "Nazario_5.csv"

data = pd.read_csv(file_path, low_memory=False)

print("Dataset shape:", data.shape)
print("\nLabel distribution:")
print(data["label"].value_counts(dropna=False))

# Check missing values in columns
print("\nMissing values:")
print(data[["subject", "body", "label"]].isnull().sum())

subject = data["subject"].fillna("").astype(str).str.strip().str.lower()
body = data["body"].fillna("").astype(str).str.strip().str.lower()

data["combined_text"] = subject + " " + body
data["combined_text"] = data["combined_text"].str.strip()

print("\nEmpty combined emails:",
      (data["combined_text"] == "").sum())

print("Duplicate combined emails:",
      data["combined_text"].duplicated().sum())

print("\nLabel counts by empty/non-empty text:")
print(
    data.assign(empty=data["combined_text"].eq(""))
    .groupby(["label", "empty"])
    .size()
)

print("\nPreparation inspection complete.")
