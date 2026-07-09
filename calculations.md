# Calculations

This document captures the main formulas used across the Snowflake ELT Warehouse project, including dashboard metrics, local CSV computations, and dbt-style aggregates.

## Raw / Local Data Calculations

These formulas are applied when the dashboard reads from local CSV files and builds the `FACT_ORDERS` dataset.

- `gross_sales = quantity * unit_price`
- `net_sales = line_total`
- `discount_value = gross_sales - net_sales`
- `status = status` (passed through unchanged)
- `payment_method = payment_method` (passed through unchanged)

## KPI Calculations

### Total Revenue
- `total_revenue = ROUND(SUM(net_sales), 2)`

### Total Orders
- `total_orders = COUNT(DISTINCT order_id)`

### Total Customers
- `total_customers = COUNT(DISTINCT customer_id)`

### Total Products
- `total_products = COUNT(DISTINCT product_id)`

### Average Order Value
- `average_order_value = ROUND(SUM(net_sales) / COUNT(DISTINCT order_id), 2)`
- If `total_orders = 0`, then `average_order_value = 0`

## Revenue Trend and Aggregations

### Monthly Revenue
- `month = DATE_TRUNC('month', order_date)`
- `net_revenue = ROUND(SUM(net_sales), 2)`
- `order_count = COUNT(DISTINCT order_id)`

### Revenue by Category
- `net_revenue = SUM(net_sales)` grouped by `category`

### Revenue by Brand
- `net_revenue = SUM(net_sales)` grouped by `brand`

### Revenue by Payment Method
- `net_revenue = SUM(net_sales)` grouped by `payment_method`

## Product Analytics

### Top Products
- `items_sold = SUM(quantity)` grouped by `product_name`, `category`, `brand`
- `net_revenue = SUM(net_sales)` grouped by `product_name`, `category`, `brand`

### Revenue by Product
- `net_revenue = SUM(net_sales)` grouped by `product_name`, `category`, `brand`
- `units_sold = SUM(quantity)` grouped by `product_name`, `category`, `brand`

### Average Selling Price
- `average_selling_price = ROUND(SUM(net_sales) / NULLIF(SUM(quantity), 0), 2)`
- This avoids division by zero using `NULLIF(SUM(quantity), 0)`.

## Customer Analytics

### Top Customers
- `order_count = COUNT(DISTINCT order_id)` grouped by customer
- `lifetime_value = SUM(net_sales)` grouped by customer
- `average_order_value = AVG(net_sales)` grouped by customer

### Average Spend Per Customer
- `average_spend = ROUND(SUM(net_sales) / COUNT(DISTINCT order_id), 2)` grouped by customer

### Repeat Customers
- `repeat_customer` is defined as customers where `COUNT(DISTINCT order_id) > 1`
- `lifetime_value = SUM(net_sales)` for repeat customers

### Customers by Country / City
- `customer_count = COUNT(DISTINCT customer_id)` grouped by `country` or by `city, country`

### New Customers by Month
- `month = DATE_TRUNC('month', signup_date)`
- `new_customers = COUNT(customer_id)` grouped by `month`

## Discount and Pricing Analytics

### Average Discount by Category
- `average_discount = AVG(discount_percent)` grouped by `category`
- `total_items = SUM(quantity)` grouped by `category`
- `total_discount_value = SUM(gross_sales - net_sales)` grouped by `category`

### Stock Levels
- `stock` is reported directly from the `DIM_PRODUCTS` table

## Filter Logic

The dashboard builds filter clauses using the following logic:

- `order_date >= start_date` when a start date filter is provided
- `order_date <= end_date` when an end date filter is provided
- `country IN (...)` when countries are selected
- `category IN (...)` when categories are selected
- `brand IN (...)` when brands are selected
- `payment_method IN (...)` when payment methods are selected
- `status IN (...)` when order statuses are selected

## Notes

- Local mode emulates SQL using pandas and standardizes column names to uppercase.
- The dashboard uses cleaned and aggregated metrics from `FACT_ORDERS`, `DIM_PRODUCTS`, and `DIM_CUSTOMERS`.
- These formulas support both Snowflake SQL and local CSV fallback computations.
