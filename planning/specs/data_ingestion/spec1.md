# Data Ingestion Spec

## Overview
Define ingestion scripts and structure for loading raw CSV files into Snowflake.

## Scope
- RAW schema table creation
- COPY INTO commands
- file format definitions
- stage setup

## Requirements
- raw table columns match source CSV fields
- scripts should be reusable for new data loads
- support Snowflake internal stage and file format

## Outputs
- `sql/03_load_data.sql`
- `sql/01_setup.sql`
- `sql/02_create_tables.sql`
