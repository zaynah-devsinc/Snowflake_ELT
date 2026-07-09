SELECT

    DATE_TRUNC('month', order_date) AS sales_month,

    COUNT(DISTINCT order_id) AS total_orders,

    SUM(quantity) AS items_sold,

    SUM(gross_sales) AS gross_revenue,

    SUM(net_sales) AS net_revenue,

    AVG(net_sales) AS average_order_value

FROM {{ ref('fact_orders') }}

GROUP BY sales_month

ORDER BY sales_month
