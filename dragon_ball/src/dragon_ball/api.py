from __future__ import annotations

from pathlib import Path

import kagglehub
from kagglehub import KaggleDatasetAdapter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "source"

DATASET = "adilshamim8/student-performance-and-learning-style"

FILE_NAME = "student_performance.csv"


def download_source(output_dir: Path = OUTPUT_DIR) -> Path:
    """Load the latest version from Kaggle and land it in data/source.
    """
    df = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS,
        DATASET,
        FILE_NAME,
    )

    print("First 5 records:")
    print(df.head())

    # create the folder if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / FILE_NAME
    df.to_csv(output_path, index=False)
    print(f"Saved to: {output_path} ({len(df):,} rows)")
    return output_path


if __name__ == "__main__":
    download_source()
