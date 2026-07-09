{{
    config(
        materialized='table'
    )
}}

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

    -- Use the raw line_total from order_items because it already reflects
    -- discounts and the seasonal order value multiplier applied during data generation.
    oi.line_total AS net_sales

FROM {{ ref('stg_orders') }} o

JOIN {{ ref('stg_order_items') }} oi
    ON o.order_id = oi.order_id

{% if is_incremental() %}

WHERE o.order_date >
(
    SELECT MAX(order_date)
    FROM {{ this }}
)

{% endif %}