from __future__ import annotations

from pathlib import Path

import kagglehub
from kagglehub import KaggleDatasetAdapter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "source"

# Name of the file INSIDE the Kaggle dataset (not a local path)
file_path = "student_performance.csv"

# Load the latest version
df = kagglehub.dataset_load(
  KaggleDatasetAdapter.PANDAS,
  "adilshamim8/student-performance-and-learning-style",
  file_path,
)

print("First 5 records:")
print(df.head())

# create the folder if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
output_path = OUTPUT_DIR / "student_performance.csv"
df.to_csv(output_path, index=False)
print(f"Saved to: {output_path}")
