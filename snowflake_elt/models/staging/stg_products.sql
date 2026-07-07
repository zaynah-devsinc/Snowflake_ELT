SELECT
    product_id,
    product_name,
    category,
    brand,
    price,
    stock
FROM {{ source('raw', 'products') }}