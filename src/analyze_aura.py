
from pathlib import Path

import pandas as pd

data_folder = Path(__file__).parent.parent / "data" / "aura"
csv_files = sorted(data_folder.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {data_folder}")

for csv_file in csv_files:
    data = pd.read_csv(csv_file, low_memory=False)

    print("\n" + "=" * 70)
    print(f"FILE: {csv_file.name}")
    print("=" * 70)

    # 1. Dataset dimensions
    print(f"Rows: {len(data):,}")
    print(f"Columns: {len(data.columns)}")

    # 2. Data types
    print("\nData types:")
    print(data.dtypes.to_string())

    # 3. Missing values
    print("\nMissing values:")
    missing = data.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        print("No missing values found.")
    else:
        print(missing.to_string())

    # 4. Duplicate rows
    print(f"\nDuplicate rows: {data.duplicated().sum():,}")

    # 5. Investigate the target labels
    if "label" in data.columns:
        print("\nLabel distribution:")
        print(data["label"].value_counts(dropna=False).to_string())

        print("\nLabel percentages:")
        print(
            (data["label"].value_counts(normalize=True, dropna=False) * 100)
            .round(2)
            .to_string()
        )
    else:
        print("\nWARNING: No column named 'label' found.")

    # 6. Check email text fields
    for column in ["subject", "body"]:
        if column in data.columns:
            text_data = data[column].fillna("").astype(str)

            print(f"\n{column}:")
            print(f"Empty values: {(text_data.str.strip() == '').sum():,}")
            print(f"Average length: {text_data.str.len().mean():.1f} characters")

    # 7. Inspect a few examples
    sample_columns = [
        col for col in ["sender", "subject", "body", "urls", "label"]
        if col in data.columns
    ]

    print("\nFirst 3 examples:")
    print(
        data[sample_columns].head(3).to_string(
            index=False,
            max_colwidth=100
        )
    )
