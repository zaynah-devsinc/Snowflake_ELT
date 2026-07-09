# Automation Spec

## Overview
Define Streams and Tasks to automate incremental processing in Snowflake.

## Scope
- stream definitions for raw / staging updates
- scheduled tasks for nightly or periodic dbt runs
- metadata tracking for incremental loads

## Requirements
- Streams should detect new rows in relevant source tables
- Tasks should orchestrate updates for staging and mart models
- include error handling and retry logic where possible

## Outputs
- `sql/04_streams.sql`
- `sql/05_tasks.sql`
