from __future__ import annotations
from pathlib import Path
from config import get_s3_client, settings

# s3 bucket
bucket = settings.bucket

# client
client = get_s3_client()

# where downloaded raw files land
# RAW_DIR = Path("data/raw")
#  Path(__file__).resolve().parent.parent.parent / data / raw
RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"

# right now I only need to get only one file
def fetch_object(key, dest_dir: Path = RAW_DIR) -> Path:
    """ Download a file from s3 and save it to dest_dir """
    # create or check if the directory exist
    dest_dir.mkdir(parents=True, exist_ok=True)
    client.download_file(bucket, key, dest_dir/ key)
    return dest_dir / key

if __name__ == "__main__":
    taco = fetch_object(settings.student_performance_key)