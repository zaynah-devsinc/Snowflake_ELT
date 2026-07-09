USE DATABASE ELT_WAREHOUSE;
USE SCHEMA RAW_MARTS;

-- Total Revenue
SELECT
    ROUND(SUM(net_sales), 2) AS total_revenue
FROM FACT_ORDERS;

-- Total Orders
SELECT
    COUNT(DISTINCT order_id) AS total_orders
FROM FACT_ORDERS;

-- Monthly Revenue
SELECT
    sales_month,
    net_revenue
FROM SALES_SUMMARY
ORDER BY sales_month;