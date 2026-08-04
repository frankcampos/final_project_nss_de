"""Publish a serving copy of the warehouse for Metabase.

Metabase runs in a container that only mounts ``data/serving`` (read-only), so
it cannot see ``data/warehouse.duckdb`` at all. It also cannot share the file:
DuckDB allows a single writer, so a BI tool holding the warehouse open would
collide with ``dbt build``. This module publishes a decoupled copy instead.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

# Anchor to this file's location so it works no matter the working directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WAREHOUSE = PROJECT_ROOT / "data" / "warehouse.duckdb"
SERVING = PROJECT_ROOT / "data" / "serving" / "warehouse.duckdb"


def publish(warehouse: Path = WAREHOUSE, serving: Path = SERVING) -> Path:
    """Copy the warehouse to the serving directory and return the new path.

    Uses DuckDB's ``COPY FROM DATABASE`` rather than a file copy. A plain copy
    can catch an un-checkpointed write-ahead log and produce a ``.duckdb`` that
    Metabase refuses to open. Staging to a temp file and swapping it in means a
    reader never sees a half-written database.
    """
    if not warehouse.exists():
        raise FileNotFoundError(f"{warehouse} not found — run `dbt build` first")

    serving.parent.mkdir(parents=True, exist_ok=True)
    staged = serving.with_name(f"{serving.name}.staging")
    staged.unlink(missing_ok=True)

    connection = duckdb.connect(str(warehouse))
    connection.execute("CHECKPOINT")
    connection.execute(f"ATTACH '{staged}' AS serving_copy")
    connection.execute("COPY FROM DATABASE warehouse TO serving_copy")
    connection.execute("DETACH serving_copy")
    connection.close()

    # Atomic on the same filesystem: Metabase either sees the old file or the
    # new one, never a partial write.
    staged.replace(serving)
    return serving


def main() -> None:
    published = publish()
    print(f"published {published} ({published.stat().st_size / 1_000_000:.1f} MB)")
    print("Metabase should point at /serving/warehouse.duckdb (path inside the container)")


if __name__ == "__main__":
    main()
