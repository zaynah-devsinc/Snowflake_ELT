-- Tasks script
CREATE OR REPLACE TASK refresh_fact_orders
WAREHOUSE = COMPUTE_WH
SCHEDULE = '5 MINUTE'
AS

MERGE INTO RAW_MARTS.FACT_ORDERS f
USING (
    SELECT
        oi.order_item_id,
        o.order_id,
        o.order_date,
        o.customer_id,
        oi.product_id,
        oi.quantity,
        oi.unit_price,
        oi.discount_percent,
        oi.line_total,
        o.status,
        o.payment_method,
        oi.quantity * oi.unit_price AS gross_sales,
        oi.quantity * oi.unit_price -
            (oi.quantity * oi.unit_price * oi.discount_percent / 100) AS net_sales
    FROM RAW.ORDERS o
    JOIN RAW.ORDER_ITEMS oi
      ON o.order_id = oi.order_id
) s
ON f.order_item_id = s.order_item_id

WHEN MATCHED THEN
UPDATE SET
    quantity = s.quantity,
    line_total = s.line_total,
    net_sales = s.net_sales

WHEN NOT MATCHED THEN
INSERT (
    order_item_id,
    order_id,
    order_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    discount_percent,
    line_total,
    status,
    payment_method,
    gross_sales,
    net_sales
)
VALUES (
    s.order_item_id,
    s.order_id,
    s.order_date,
    s.customer_id,
    s.product_id,
    s.quantity,
    s.unit_price,
    s.discount_percent,
    s.line_total,
    s.status,
    s.payment_method,
    s.gross_sales,
    s.net_sales
);

ALTER TASK refresh_fact_orders RESUME;

SHOW TASKS;