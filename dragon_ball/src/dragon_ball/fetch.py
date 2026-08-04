from __future__ import annotations

from pathlib import Path

from dragon_ball.config import get_s3_client, settings

# where downloaded raw files land
RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"


# right now I only need to get only one file
def fetch_object(key: str | None = None, dest_dir: Path = RAW_DIR) -> Path:
    """ Download a file from s3 and save it to dest_dir """
    key = key or settings.student_performance_key
    client = get_s3_client()

    # create or check if the directory exist
    dest_dir.mkdir(parents=True, exist_ok=True)
    destination = dest_dir / key
    client.download_file(settings.bucket, key, str(destination))
    print(f"downloaded s3://{settings.bucket}/{key} -> {destination}")
    return destination


if __name__ == "__main__":
    fetch_object(settings.student_performance_key)
