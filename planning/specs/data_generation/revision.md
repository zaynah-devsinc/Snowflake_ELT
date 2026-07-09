# Data Generation Revision

## Notes
- Confirmed generator uses Faker and writes all raw CSV files to `data/raw/`.
- Verified customer, product, order, and order item records are created.
- Ensure output schema matches downstream dbt staging expectations.

## Updates
- Add `discount_percent` and `line_total` to order item output.
- Keep `order_date` and `signup_date` as date fields.
