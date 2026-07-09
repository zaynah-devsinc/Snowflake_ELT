SELECT
    customer_id,
    first_name,
    last_name,
    email,
    city,
    country,
    signup_date,

    DATEDIFF('day', signup_date, CURRENT_DATE()) AS customer_age_days

FROM {{ ref('stg_customers') }}