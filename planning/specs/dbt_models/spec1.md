# dbt Models Spec

## Overview
Design dbt models for staging and marts using a Medallion Architecture.

## Scope
- staging models for clean / normalized data
- mart models for dimensions and facts
- sources and schema configuration
- dbt tests for data quality

## Requirements
- use `source()` for raw tables and `ref()` for dbt models
- create `stg_customers`, `stg_products`, `stg_orders`, `stg_order_items`
- create `dim_customers`, `dim_products`, `dim_date`, `fact_orders`
- add `unique`, `not_null`, and `relationships` tests

## Outputs
- `dbt/models/staging/`
- `dbt/models/marts/`
- `dbt_project.yml`
- `dbt/models/staging/sources.yml`
