SELECT
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_percent,
    line_total
FROM {{ source('raw', 'order_items') }}