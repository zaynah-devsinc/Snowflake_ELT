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
    o.payment_method

FROM {{ ref('stg_orders') }} o

JOIN {{ ref('stg_order_items') }} oi
ON o.order_id = oi.order_id