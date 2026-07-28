from __future__ import annotations

from pathlib import Path

from botocore.exceptions import ClientError
from config import get_s3_client, settings

# Anchor to this file's location so it works no matter the working directory.
SOURCE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "source"

def ensure_bucket(client, bucket: str) -> None:
    try:
        client.head_bucket(Bucket=bucket)
        print(f"bucket '{bucket}' already exists")
    except ClientError:
        client.create_bucket(Bucket=bucket)
        print(f"created bucket '{bucket}'")

def upload(client, bucket: str, local_path: Path, key: str) -> None:
    if not local_path.exists():
        raise FileNotFoundError(
            f"{local_path} not found — run apy.py first"
        )
    client.upload_file(str(local_path), bucket, key)
    size = local_path.stat().st_size
    print(f"uploaded {local_path} -> s3://{bucket}/{key} ({size:,} bytes)")


def main() -> None:
    client = get_s3_client()
    ensure_bucket(client, settings.bucket)
    upload(client, settings.bucket, SOURCE_DIR / "student_performance.csv", settings.student_performance_key)
    print(f"\ndone. endpoint={settings.endpoint_url} bucket={settings.bucket}")


if __name__ == "__main__":
    main()
