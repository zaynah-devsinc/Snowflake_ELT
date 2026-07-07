SELECT
    product_id,
    product_name,
    category,
    brand,
    price
FROM {{ ref('stg_products') }}