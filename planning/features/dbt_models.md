# dbt Models

Feature: Define dbt staging and marts models using the Medallion Architecture.

Deliverables:
- Staging models in `dbt/models/staging/`
- Mart models in `dbt/models/marts/`
- `dbt_project.yml` and sources definitions
- tests for uniqueness, not_null, and relationships

Key elements:
- clean and standardize raw datasets
- create dimensional tables and fact tables
- use `ref()` and `source()` for dependencies
- incremental model patterns for large datasets
