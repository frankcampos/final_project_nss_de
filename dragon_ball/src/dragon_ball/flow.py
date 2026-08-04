

from __future__ import annotations


from contextlib import chdir
from pathlib import Path

import prefect
from prefect.logging import get_run_logger
from prefect import flow
from prefect_dbt import PrefectDbtRunner
from dbt.adapters.duckdb.connections import DuckDBConnectionManager

from dragon_ball import api, fetch, publish as publish_module, seed

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DBT_DIR = PROJECT_ROOT / "dragon_ball_dbt"


@prefect.task(retries=3, retry_delay_seconds=5)
def get_source_data() -> str:
    """Pull the latest dataset from Kaggle into data/source."""
    logger = get_run_logger()
    path = api.download_source()
    logger.info(f"source data downloaded from Kaggle -> {path}")
    return str(path)


@prefect.task(retries=3, retry_delay_seconds=5)
def seed_data() -> None:
    """Upload data/source to the S3 bucket, creating it if needed."""
    logger = get_run_logger()
    seed.main()
    logger.info("source file seeded into the object store")


@prefect.task(retries=3, retry_delay_seconds=5)
def fetch_data() -> str:
    """Download the object back out of S3 into data/raw, where dbt reads it."""
    logger = get_run_logger()
    path = fetch.fetch_object()
    logger.info(f"raw data fetched from S3 -> {path}")
    return str(path)

@prefect.task
def run_dbt() -> None:
    """`dbt build` — seeds, models and tests, in dependency order.

    dbt resolves the paths in profiles.yml relative to the working directory, so
    this runs with cwd=dragon_ball_dbt. Running it from anywhere else silently
    creates a fresh empty database instead of using the warehouse.
    """
    try:
        with chdir(DBT_DIR):
            PrefectDbtRunner().invoke(["build"])
    finally:
        # dbt-duckdb caches its connection in a class-level singleton that
        # survives dbt's own teardown; close it so publish can re-attach the file.
        env = DuckDBConnectionManager._ENV
        if env is not None:
            env.close()
        DuckDBConnectionManager.close_all_connections()


@prefect.task
def publish() -> str:
    """Copy the warehouse to the serving DuckDB Metabase reads."""
    logger = get_run_logger()
    published = publish_module.publish()
    logger.info(f"serving layer published -> {published}")
    return str(published)


@prefect.flow(log_prints=True)
def run_pipeline() -> None:
    """Kaggle to dashboard, in order. Each call below is a tracked task run."""
    logger = get_run_logger()
    get_source_data()
    seed_data()
    fetch_data()
    run_dbt()
    publish()

    logger.info("pipeline complete - Metabase is reading the freshly published data")


if __name__ == "__main__":
    # run pipeline
    # run_pipeline.serve(name="nightly-orders", cron="0 6 * * *")
    run_pipeline.serve()
