SELECT
    order_id,
    customer_id,
    order_date,
    status,
    payment_method
FROM {{ source('raw', 'orders') }}