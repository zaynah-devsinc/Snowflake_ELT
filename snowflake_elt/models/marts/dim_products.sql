SELECT
    product_id,
    product_name,
    category,
    brand,
    price,
    stock,

    CASE
        WHEN price < 50 THEN 'Budget'
        WHEN price < 150 THEN 'Mid Range'
        ELSE 'Premium'
    END AS price_segment

FROM {{ ref('stg_products') }}