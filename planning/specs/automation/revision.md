# Automation Revision

## Notes
- Streams should identify new data in RAW and STAGING layers.
- Tasks should trigger dbt runs or SQL processing on a schedule.
- Review task dependencies and execution order.

## Updates
- Add task scheduling cadence (e.g. hourly, daily).
- Ensure task statements reference the correct Snowflake warehouse and role.
