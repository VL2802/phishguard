from pathlib import Path

import pandas as pd

data_folder = Path(__file__).parent.parent / "data" / "aura"
csv_files = sorted(data_folder.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {data_folder}")

summary = []

for csv_file in csv_files:
    data = pd.read_csv(csv_file)
    rows, columns = data.shape

    print(f"\nFilename: {csv_file.name}")
    print(f"Rows: {rows:,}")
    print(f"Columns: {columns}")
    print(f"Column names: {list(data.columns)}")

    summary.append(
        {
            "dataset": csv_file.name,
            "rows": rows,
            "columns": columns,
        }
    )

print("\nSummary:")
print(pd.DataFrame(summary).to_string(index=False))

first_data = pd.read_csv(csv_files[0])
print(f"\nFirst 5 rows of {csv_files[0].name}:")
print(first_data.head())
