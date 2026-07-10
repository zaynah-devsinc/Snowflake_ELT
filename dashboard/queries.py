from datetime import date


def _quote_value(value):
    if isinstance(value, date):
        return f"'{value.isoformat()}'"
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def _format_list(values):
    if not values:
        return None
    return ", ".join(_quote_value(value) for value in values)


def _build_filter_clause(filters: dict, alias: str = "f") -> str:
    clauses = ["1=1"]

    if filters.get("start_date"):
        clauses.append(f"{alias}.order_date >= {_quote_value(filters['start_date'])}")
    if filters.get("end_date"):
        clauses.append(f"{alias}.order_date <= {_quote_value(filters['end_date'])}")

    if filters.get("countries"):
        values = _format_list(filters["countries"])
        clauses.append(f"c.country IN ({values})")
    if filters.get("categories"):
        values = _format_list(filters["categories"])
        clauses.append(f"p.category IN ({values})")
    if filters.get("brands"):
        values = _format_list(filters["brands"])
        clauses.append(f"p.brand IN ({values})")
    if filters.get("payment_methods"):
        values = _format_list(filters["payment_methods"])
        clauses.append(f"f.payment_method IN ({values})")
    if filters.get("statuses"):
        values = _format_list(filters["statuses"])
        clauses.append(f"f.status IN ({values})")

    return " AND ".join(clauses)


def get_base_order_query(filters: dict, limit: int | None = None) -> str:
    where_clause = _build_filter_clause(filters)
    query = f"""
SELECT
    f.order_id,
    f.order_date,
    f.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    c.city,
    c.country,
    f.product_id,
    p.product_name,
    p.category,
    p.brand,
    p.price AS product_price,
    f.quantity,
    f.discount_percent,
    f.line_total,
    f.gross_sales,
    f.net_sales,
    f.status,
    f.payment_method
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
ORDER BY f.order_date DESC
"""
    if limit:
        query += f"LIMIT {limit}\n"
    return query


def get_kpi_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    ROUND(SUM(f.net_sales), 2) AS total_revenue,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_id) AS total_customers,
    COUNT(DISTINCT f.product_id) AS total_products,
    ROUND(CASE WHEN COUNT(DISTINCT f.order_id) = 0 THEN 0 ELSE SUM(f.net_sales) / COUNT(DISTINCT f.order_id) END, 2) AS average_order_value
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
"""


def get_monthly_revenue_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    DATE_TRUNC('month', f.order_date) AS month,
    ROUND(SUM(f.net_sales), 2) AS net_revenue,
    COUNT(DISTINCT f.order_id) AS order_count
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
GROUP BY month
ORDER BY month
"""


def get_category_revenue_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    p.category AS category,
    SUM(f.net_sales) AS net_revenue
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
GROUP BY p.category
ORDER BY net_revenue DESC
"""


def get_status_distribution_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    f.status AS status,
    COUNT(*) AS count
FROM FACT_ORDERS f
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
WHERE {where_clause}
GROUP BY f.status
ORDER BY count DESC
"""


def get_sales_by_brand_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    p.brand AS brand,
    SUM(f.net_sales) AS net_revenue
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
GROUP BY p.brand
ORDER BY net_revenue DESC
"""


def get_top_products_query(filters: dict, limit: int = 10) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    p.product_name AS product_name,
    p.category AS category,
    p.brand AS brand,
    SUM(f.quantity) AS items_sold,
    SUM(f.net_sales) AS net_revenue
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
GROUP BY p.product_name, p.category, p.brand
ORDER BY net_revenue DESC
LIMIT {limit}
"""


def get_revenue_by_payment_method_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    f.payment_method AS payment_method,
    SUM(f.net_sales) AS net_revenue
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
GROUP BY f.payment_method
ORDER BY net_revenue DESC
"""


def get_discount_analysis_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    p.category AS category,
    AVG(f.discount_percent) AS average_discount,
    SUM(f.quantity) AS total_items,
    SUM(f.gross_sales - f.net_sales) AS total_discount_value
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
GROUP BY p.category
ORDER BY total_discount_value DESC
"""


def get_daily_sales_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    DATE_TRUNC('day', f.order_date) AS day,
    SUM(f.net_sales) AS net_revenue,
    COUNT(DISTINCT f.order_id) AS order_count
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
GROUP BY day
ORDER BY day
"""


def get_top_customers_query(filters: dict, limit: int | None = 20) -> str:
    where_clause = _build_filter_clause(filters)
    query = f"""
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    c.city,
    c.country,
    COUNT(DISTINCT f.order_id) AS order_count,
    SUM(f.net_sales) AS lifetime_value,
    ROUND(SUM(f.net_sales) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS average_order_value
FROM FACT_ORDERS f
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
WHERE {where_clause}
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.city, c.country
ORDER BY lifetime_value DESC
"""
    if limit is not None:
        query += f"LIMIT {limit}\n"
    return query


def get_customers_by_country_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    c.country AS country,
    COUNT(DISTINCT c.customer_id) AS customer_count
FROM FACT_ORDERS f
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
WHERE {where_clause}
GROUP BY c.country
ORDER BY customer_count DESC
"""


def get_customers_by_city_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    c.city AS city,
    c.country AS country,
    COUNT(DISTINCT c.customer_id) AS customer_count
FROM FACT_ORDERS f
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
WHERE {where_clause}
GROUP BY c.city, c.country
ORDER BY customer_count DESC
LIMIT 50
"""


def get_new_customers_query(filters: dict) -> str:
    clauses = ["1=1"]
    if filters.get("start_date"):
        clauses.append(f"signup_date >= {_quote_value(filters['start_date'])}")
    if filters.get("end_date"):
        clauses.append(f"signup_date <= {_quote_value(filters['end_date'])}")
    if filters.get("countries"):
        values = _format_list(filters["countries"])
        clauses.append(f"country IN ({values})")
    if filters.get("categories") or filters.get("brands"):
        clauses.append("customer_id IN (SELECT customer_id FROM FACT_ORDERS f LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id WHERE " + _build_filter_clause(filters) + ")")

    filter_clause = " AND ".join(clauses)
    return f"""
SELECT
    DATE_TRUNC('month', signup_date) AS month,
    COUNT(customer_id) AS new_customers
FROM DIM_CUSTOMERS
WHERE {filter_clause}
GROUP BY month
ORDER BY month
"""


def get_repeat_customers_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.country AS country,
    COUNT(DISTINCT f.order_id) AS order_count,
    SUM(f.net_sales) AS lifetime_value
FROM FACT_ORDERS f
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
WHERE {where_clause}
GROUP BY c.customer_id, c.first_name, c.last_name, c.country
HAVING COUNT(DISTINCT f.order_id) > 1
ORDER BY order_count DESC
LIMIT 50
"""


def get_average_spend_per_customer_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.country AS country,
    ROUND(SUM(f.net_sales) / COUNT(DISTINCT f.order_id), 2) AS average_spend
FROM FACT_ORDERS f
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
WHERE {where_clause}
GROUP BY c.customer_id, c.first_name, c.last_name, c.country
ORDER BY average_spend DESC
LIMIT 50
"""


def get_products_by_category_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    p.category AS category,
    COUNT(DISTINCT p.product_id) AS product_count
FROM DIM_PRODUCTS p
LEFT JOIN FACT_ORDERS f ON p.product_id = f.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
GROUP BY p.category
ORDER BY product_count DESC
"""


def get_stock_levels_query(filters: dict) -> str:
    categories = _format_list(filters.get("categories", []))
    brands = _format_list(filters.get("brands", []))
    clauses = ["1=1"]
    if categories:
        clauses.append(f"category IN ({categories})")
    if brands:
        clauses.append(f"brand IN ({brands})")
    clause = " AND ".join(clauses)
    return f"""
SELECT
    product_id,
    product_name,
    category,
    brand,
    stock
FROM DIM_PRODUCTS
WHERE {clause}
ORDER BY stock ASC
LIMIT 50
"""


def get_revenue_by_product_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    p.product_name AS product_name,
    p.category AS category,
    p.brand AS brand,
    SUM(f.net_sales) AS net_revenue,
    SUM(f.quantity) AS units_sold
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
GROUP BY p.product_name, p.category, p.brand
ORDER BY net_revenue DESC
LIMIT 50
"""


def get_average_selling_price_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    p.product_name AS product_name,
    p.category AS category,
    p.brand AS brand,
    ROUND(SUM(f.net_sales) / NULLIF(SUM(f.quantity), 0), 2) AS average_selling_price
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
GROUP BY p.product_name, p.category, p.brand
ORDER BY average_selling_price DESC
LIMIT 50
"""


def get_category_distribution_query(filters: dict) -> str:
    where_clause = _build_filter_clause(filters)
    return f"""
SELECT
    p.category AS category,
    COUNT(DISTINCT p.product_id) AS product_count
FROM DIM_PRODUCTS p
LEFT JOIN FACT_ORDERS f ON p.product_id = f.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
WHERE {where_clause}
GROUP BY p.category
ORDER BY product_count DESC
"""


def get_filter_options_query() -> str:
    return """
SELECT
    ARRAY_AGG(DISTINCT c.country) AS countries,
    ARRAY_AGG(DISTINCT p.category) AS categories,
    ARRAY_AGG(DISTINCT p.brand) AS brands,
    ARRAY_AGG(DISTINCT f.payment_method) AS payment_methods,
    ARRAY_AGG(DISTINCT f.status) AS statuses,
    MIN(f.order_date) AS min_order_date,
    MAX(f.order_date) AS max_order_date
FROM FACT_ORDERS f
LEFT JOIN DIM_PRODUCTS p ON f.product_id = p.product_id
LEFT JOIN DIM_CUSTOMERS c ON f.customer_id = c.customer_id
"""
