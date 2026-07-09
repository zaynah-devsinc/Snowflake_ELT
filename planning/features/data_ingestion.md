# Data Ingestion

Feature: Ingest raw CSV datasets into Snowflake RAW schema.

Deliverables:
- SQL scripts for RAW table creation
- `sql/03_load_data.sql`
- Snowflake COPY INTO statements
- file format and stage definitions

Key elements:
- raw table schemas that match source CSVs
- secure Snowflake stage configuration
- loading using bulk COPY INTO
- data validation queries for loaded records
