# Pipeline entry points. Run from the dragon_ball/ directory.
#
# dbt resolves the paths in profiles.yml relative to the working directory, so
# every dbt target cds into dragon_ball_dbt first. Running dbt from anywhere
# else silently creates a fresh empty database instead of using the warehouse.

DBT := cd dragon_ball_dbt && uv run dbt

.PHONY: help build publish refresh test docs clean

help:
	@echo "make refresh  - build the warehouse, then publish the serving copy (use this)"
	@echo "make build    - dbt build only"
	@echo "make publish  - copy warehouse -> data/serving for Metabase"
	@echo "make test     - dbt test only"
	@echo "make docs     - generate and serve dbt docs"
	@echo "make clean    - remove dbt target/ and the serving copy"

# The one to run. Publishing separately is what gets forgotten, which leaves
# Metabase reading a stale snapshot with no indication anything is wrong.
refresh: build publish

build:
	$(DBT) build

publish:
	uv run publish-serving

test:
	$(DBT) test

docs:
	$(DBT) docs generate && $(DBT) docs serve

clean:
	$(DBT) clean
	rm -f data/serving/warehouse.duckdb data/serving/warehouse.duckdb.staging
