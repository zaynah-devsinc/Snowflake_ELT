# Data Ingestion Revision

## Notes
- Raw ingestion should use `COPY INTO` from staged CSV files.
- Confirm columns and data types in RAW tables align with generated CSV files.
- Review loading scripts for Snowflake compatibility.

## Updates
- Add schema names and file format definitions where needed.
- Make sure stage paths are parameterized if possible.
