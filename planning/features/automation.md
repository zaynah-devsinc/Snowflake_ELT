# Automation

Feature: Automate incremental data processing using Snowflake Streams and Tasks.

Deliverables:
- `sql/04_streams.sql`
- `sql/05_tasks.sql`
- Snowflake task definitions for downstream execution
- incremental dbt model triggers

Key elements:
- Streams to detect new rows in `RAW` or `STAGING`
- Tasks to orchestrate periodic loads and transformations
- incremental refresh logic and metadata tracking
