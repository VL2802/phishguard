
from pathlib import Path

import pandas as pd

data_folder = Path(__file__).parent.parent / "data" / "aura"

for csv_file in sorted(data_folder.glob("*.csv")):
    data = pd.read_csv(csv_file, low_memory=False)

    print(f"\n{'=' * 60}")
    print(f"Dataset: {csv_file.name}")
    print("Label counts:")
    print(data["label"].value_counts(dropna=False).sort_index())

    for label in sorted(data["label"].dropna().unique()):
        examples = data.loc[
            data["label"] == label,
            ["subject", "body"]
        ].head(3)

        print(f"\nExamples for label {label}:")
        for _, row in examples.iterrows():
            subject = str(row["subject"])[:120]
            body = str(row["body"])[:250]

            print(f"Subject: {subject}")
            print(f"Body: {body}")
            print("-" * 30)
