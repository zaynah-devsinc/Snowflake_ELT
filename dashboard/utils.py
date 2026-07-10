import os
from datetime import date
from pathlib import Path

import pandas as pd
import snowflake.connector
import streamlit as st


def _load_snowflake_config() -> dict:
    try:
        return st.secrets.get("snowflake", {})
    except Exception:
        return {}


def _get_local_csv_root() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "raw"


def _has_snowflake_config() -> bool:
    try:
        _validate_snowflake_config(_load_snowflake_config())
        return True
    except ValueError:
        return False


def _is_local_mode() -> bool:
    if _has_snowflake_config():
        return False

    data_root = _get_local_csv_root()
    return data_root.exists() and any(data_root.glob("*.csv"))


def is_local_mode() -> bool:
    return _is_local_mode()


def _validate_snowflake_config(config: dict) -> dict:
    placeholders = {
        "YOUR_SNOWFLAKE_USER",
        "YOUR_SNOWFLAKE_PASSWORD",
        "YOUR_SNOWFLAKE_ACCOUNT",
        "YOUR_SNOWFLAKE_WAREHOUSE",
        "YOUR_SNOWFLAKE_ROLE",
    }

    normalized = {
        "user": config.get("user") or os.getenv("SNOWFLAKE_USER"),
        "password": config.get("password") or os.getenv("SNOWFLAKE_PASSWORD"),
        "account": config.get("account") or os.getenv("SNOWFLAKE_ACCOUNT"),
        "warehouse": config.get("warehouse") or os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": config.get("database") or os.getenv("SNOWFLAKE_DATABASE", "ELT_WAREHOUSE"),
        "schema": config.get("schema") or os.getenv("SNOWFLAKE_SCHEMA", "RAW_MARTS"),
        "role": config.get("role") or os.getenv("SNOWFLAKE_ROLE"),
    }

    if not normalized["user"] or normalized["user"] in placeholders:
        raise ValueError(
            "Snowflake user is not configured. Set snowflake.user in .streamlit/secrets.toml "
            "or the SNOWFLAKE_USER environment variable."
        )

    if not normalized["password"] or normalized["password"] in placeholders:
        raise ValueError(
            "Snowflake password is not configured. Set snowflake.password in .streamlit/secrets.toml "
            "or the SNOWFLAKE_PASSWORD environment variable."
        )

    if not normalized["account"] or normalized["account"] in placeholders:
        raise ValueError(
            "Snowflake account is not configured or is still a placeholder. "
            "Use the account locator only, such as 'abc12345' or 'abc12345.us-east-1'. "
            "Do not include 'https://' or '.snowflakecomputing.com'."
        )

    if not normalized["warehouse"] or normalized["warehouse"] in placeholders:
        raise ValueError(
            "Snowflake warehouse is not configured. Set snowflake.warehouse in .streamlit/secrets.toml "
            "or the SNOWFLAKE_WAREHOUSE environment variable."
        )

    return normalized


@st.cache_resource(show_spinner=False)
def get_snowflake_connection() -> snowflake.connector.SnowflakeConnection:
    if _is_local_mode():
        raise RuntimeError("Local CSV mode enabled: Snowflake connection is not required.")

    snowflake_config = _load_snowflake_config()
    connection_args = _validate_snowflake_config(snowflake_config)
    connection_args["client_session_keep_alive"] = True
    return snowflake.connector.connect(**connection_args)


def _load_csv_data(filename: str, parse_dates=None):
    path = _get_local_csv_root() / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, parse_dates=parse_dates)


def _normalize_local_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [col.upper() if isinstance(col, str) else col for col in df.columns]
    return df


@st.cache_data(show_spinner=False, ttl=300)
def run_query(query: str) -> pd.DataFrame:
    if _is_local_mode():
        if any(token in query for token in ["FROM FACT_ORDERS", "FROM FACT_ORDERS f", "FROM DIM_PRODUCTS", "FROM DIM_CUSTOMERS"]):
            orders = _load_csv_data("orders.csv", parse_dates=["order_date"])
            items = _load_csv_data("order_items.csv")
            customers = _load_csv_data("customers.csv", parse_dates=["signup_date"])
            products = _load_csv_data("products.csv")

            if orders.empty or items.empty or products.empty or customers.empty:
                return pd.DataFrame()

            fact_orders = items.merge(orders, on="order_id", how="left")
            fact_orders["gross_sales"] = fact_orders["quantity"] * fact_orders["unit_price"]
            fact_orders["net_sales"] = fact_orders["line_total"]
            fact_orders["status"] = fact_orders["status"]
            fact_orders["payment_method"] = fact_orders["payment_method"]

            merged = fact_orders.merge(products, on="product_id", how="left")
            merged = merged.merge(customers, on="customer_id", how="left")

            # Basic SQL emulation for queries used by dashboard
            if "get_filter_options_query" in query or "ARRAY_AGG" in query:
                countries = sorted(merged["country"].dropna().unique().tolist())
                categories = sorted(merged["category"].dropna().unique().tolist())
                brands = sorted(merged["brand"].dropna().unique().tolist())
                payment_methods = sorted(merged["payment_method"].dropna().unique().tolist())
                statuses = sorted(merged["status"].dropna().unique().tolist())
                min_date = merged["order_date"].min()
                max_date = merged["order_date"].max()
                return pd.DataFrame([{"COUNTRIES": countries, "CATEGORIES": categories, "BRANDS": brands, "PAYMENT_METHODS": payment_methods, "STATUSES": statuses, "MIN_ORDER_DATE": min_date, "MAX_ORDER_DATE": max_date}])

            if "COUNT(DISTINCT f.order_id) AS total_orders" in query:
                total_revenue = merged["net_sales"].sum()
                total_orders = merged["order_id"].nunique()
                total_customers = merged["customer_id"].nunique()
                total_products = merged["product_id"].nunique()
                average_order_value = (merged["net_sales"].sum() / total_orders) if total_orders else 0
                result = pd.DataFrame([{
                    "TOTAL_REVENUE": round(total_revenue, 2),
                    "TOTAL_ORDERS": total_orders,
                    "TOTAL_CUSTOMERS": total_customers,
                    "TOTAL_PRODUCTS": total_products,
                    "AVERAGE_ORDER_VALUE": round(average_order_value, 2),
                }])
                return _normalize_local_columns(result)

            if "DATE_TRUNC('month', f.order_date) AS month" in query:
                monthly = merged.groupby(pd.Grouper(key="order_date", freq="ME")).agg({"net_sales": "sum", "order_id": pd.Series.nunique}).reset_index()
                monthly.columns = ["MONTH", "NET_REVENUE", "ORDER_COUNT"]
                return _normalize_local_columns(monthly.sort_values("MONTH"))

            if "p.product_name AS product_name" in query and "SUM(f.quantity) AS items_sold" in query:
                result = merged.groupby(["product_name", "category", "brand"]).agg(ITEMS_SOLD=("quantity", "sum"), NET_REVENUE=("net_sales", "sum")).reset_index()
                result.rename(columns={"product_name": "PRODUCT_NAME", "category": "CATEGORY", "brand": "BRAND"}, inplace=True)
                return _normalize_local_columns(result)

            if "p.product_name AS product_name" in query and "SUM(f.quantity) AS units_sold" in query:
                result = merged.groupby(["product_name", "category", "brand"]).agg(UNITS_SOLD=("quantity", "sum"), NET_REVENUE=("net_sales", "sum")).reset_index()
                result.rename(columns={"product_name": "PRODUCT_NAME", "category": "CATEGORY", "brand": "BRAND"}, inplace=True)
                return _normalize_local_columns(result)

            if "p.product_name AS product_name" in query and "SUM(f.quantity) AS units_sold" in query:
                result = merged.groupby(["product_name", "category", "brand"]).agg(UNITS_SOLD=("quantity", "sum"), NET_REVENUE=("net_sales", "sum")).reset_index()
                result.rename(columns={"product_name": "PRODUCT_NAME", "category": "CATEGORY", "brand": "BRAND"}, inplace=True)
                return _normalize_local_columns(result)

            if "p.category AS category" in query and "SUM(f.net_sales) AS net_revenue" in query and "p.product_name AS product_name" not in query:
                result = merged.groupby("category")["net_sales"].sum().reset_index(name="NET_REVENUE").sort_values("NET_REVENUE", ascending=False)
                result.rename(columns={"category": "CATEGORY"}, inplace=True)
                return _normalize_local_columns(result)

            if "COUNT(DISTINCT p.product_id) AS product_count" in query:
                result = merged.groupby("category").agg(PRODUCT_COUNT=("product_id", pd.Series.nunique)).reset_index().rename(columns={"category": "CATEGORY"}).sort_values("PRODUCT_COUNT", ascending=False)
                return _normalize_local_columns(result)

            if "c.city AS city" in query and "COUNT(DISTINCT c.customer_id) AS customer_count" in query:
                result = merged.groupby(["city", "country"]).agg(CUSTOMER_COUNT=("customer_id", pd.Series.nunique)).reset_index()
                result.rename(columns={"city": "CITY", "country": "COUNTRY"}, inplace=True)
                return _normalize_local_columns(result)

            if "f.status AS status" in query and "COUNT(*) AS count" in query:
                result = merged.groupby("status").size().reset_index(name="COUNT").sort_values("COUNT", ascending=False)
                result.rename(columns={"status": "STATUS"}, inplace=True)
                return _normalize_local_columns(result)

            if "p.brand AS brand" in query and "SUM(f.net_sales) AS net_revenue" in query:
                result = merged.groupby("brand")["net_sales"].sum().reset_index(name="NET_REVENUE").sort_values("NET_REVENUE", ascending=False)
                result.rename(columns={"brand": "BRAND"}, inplace=True)
                return _normalize_local_columns(result)

            if "p.product_name AS product_name" in query and "SUM(f.quantity) AS items_sold" in query:
                result = merged.groupby(["product_name", "category", "brand"]).agg(ITEMS_SOLD=("quantity", "sum"), NET_REVENUE=("net_sales", "sum")).reset_index()
                result.rename(columns={"product_name": "PRODUCT_NAME", "category": "CATEGORY", "brand": "BRAND"}, inplace=True)
                return _normalize_local_columns(result)

            if "ROUND(SUM(f.net_sales) / NULLIF(SUM(f.quantity), 0), 2) AS average_selling_price" in query:
                grouped = merged.groupby(["product_name", "category", "brand"]).agg(TOTAL_REVENUE=("net_sales", "sum"), TOTAL_QUANTITY=("quantity", "sum")).reset_index()
                grouped["AVERAGE_SELLING_PRICE"] = grouped.apply(lambda row: round(row["TOTAL_REVENUE"] / row["TOTAL_QUANTITY"], 2) if row["TOTAL_QUANTITY"] else 0, axis=1)
                grouped.rename(columns={"product_name": "PRODUCT_NAME", "category": "CATEGORY", "brand": "BRAND"}, inplace=True)
                return _normalize_local_columns(grouped[["PRODUCT_NAME", "CATEGORY", "BRAND", "AVERAGE_SELLING_PRICE"]])

            if "f.payment_method AS payment_method" in query:
                result = merged.groupby("payment_method")["net_sales"].sum().reset_index(name="NET_REVENUE").sort_values("NET_REVENUE", ascending=False)
                result.rename(columns={"payment_method": "PAYMENT_METHOD"}, inplace=True)
                return _normalize_local_columns(result)

            if "AVG(f.discount_percent) AS average_discount" in query:
                result = merged.groupby("category").agg({"discount_percent": "mean", "quantity": "sum", "gross_sales": lambda x: x.sum(), "net_sales": lambda x: x.sum()}).reset_index().rename(columns={"category": "CATEGORY", "discount_percent": "AVERAGE_DISCOUNT", "quantity": "TOTAL_ITEMS", "gross_sales": "TOTAL_DISCOUNT_VALUE", "net_sales": "NET_REVENUE"})
                return _normalize_local_columns(result)

            if "DATE_TRUNC('day', f.order_date) AS day" in query:
                daily = merged.groupby(pd.Grouper(key="order_date", freq="D")).agg({"net_sales": "sum", "order_id": pd.Series.nunique}).reset_index()
                daily.columns = ["DAY", "NET_REVENUE", "ORDER_COUNT"]
                return _normalize_local_columns(daily.sort_values("DAY"))

            if "HAVING COUNT(DISTINCT f.order_id) > 1" in query:
                result = merged.groupby(["customer_id", "first_name", "last_name", "country"]).agg(ORDER_COUNT=("order_id", pd.Series.nunique), LIFETIME_VALUE=("net_sales", "sum")).reset_index()
                result["CUSTOMER_NAME"] = result["first_name"] + " " + result["last_name"]
                result.rename(columns={"country": "COUNTRY"}, inplace=True)
                return _normalize_local_columns(result[["customer_id", "CUSTOMER_NAME", "COUNTRY", "ORDER_COUNT", "LIFETIME_VALUE"]])

            if "ROUND(SUM(f.net_sales) / COUNT(DISTINCT f.order_id), 2) AS average_spend" in query:
                grouped = merged.groupby(["customer_id", "first_name", "last_name", "country"]).agg(TOTAL_REVENUE=("net_sales", "sum"), ORDER_COUNT=("order_id", pd.Series.nunique)).reset_index()
                grouped["AVERAGE_SPEND"] = grouped.apply(lambda row: round(row["TOTAL_REVENUE"] / row["ORDER_COUNT"], 2) if row["ORDER_COUNT"] else 0, axis=1)
                grouped["CUSTOMER_NAME"] = grouped["first_name"] + " " + grouped["last_name"]
                grouped.rename(columns={"country": "COUNTRY"}, inplace=True)
                return _normalize_local_columns(grouped[["customer_id", "CUSTOMER_NAME", "COUNTRY", "AVERAGE_SPEND"]])

            if "COUNT(DISTINCT f.order_id) AS order_count" in query and "SUM(f.net_sales) AS lifetime_value" in query and "ROUND(SUM(f.net_sales) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS average_order_value" in query:
                grouped = merged.groupby(["customer_id", "first_name", "last_name", "email", "city", "country"]).agg(TOTAL_REVENUE=("net_sales", "sum"), ORDER_COUNT=("order_id", pd.Series.nunique)).reset_index()
                grouped["AVERAGE_ORDER_VALUE"] = grouped.apply(lambda row: round(row["TOTAL_REVENUE"] / row["ORDER_COUNT"], 2) if row["ORDER_COUNT"] else 0, axis=1)
                grouped["CUSTOMER_NAME"] = grouped["first_name"] + " " + grouped["last_name"]
                grouped.rename(columns={"email": "EMAIL", "city": "CITY", "country": "COUNTRY"}, inplace=True)
                return _normalize_local_columns(grouped[["customer_id", "CUSTOMER_NAME", "EMAIL", "CITY", "COUNTRY", "ORDER_COUNT", "TOTAL_REVENUE", "AVERAGE_ORDER_VALUE"]].rename(columns={"TOTAL_REVENUE": "LIFETIME_VALUE"}))

            if "COUNT(DISTINCT c.customer_id) AS customer_count" in query and "FROM FACT_ORDERS" in query:
                result = merged.groupby("country").agg({"customer_id": pd.Series.nunique}).reset_index().rename(columns={"country": "COUNTRY", "customer_id": "CUSTOMER_COUNT"}).sort_values("CUSTOMER_COUNT", ascending=False)
                return _normalize_local_columns(result)

            if "f.order_id" in query and "ORDER BY f.order_date DESC" in query:
                result = merged.copy()
                result["customer_name"] = result["first_name"].fillna("") + " " + result["last_name"].fillna("")
                result = result.rename(columns={
                    "order_id": "ORDER_ID",
                    "order_date": "ORDER_DATE",
                    "customer_id": "CUSTOMER_ID",
                    "customer_name": "CUSTOMER_NAME",
                    "email": "EMAIL",
                    "city": "CITY",
                    "country": "COUNTRY",
                    "product_id": "PRODUCT_ID",
                    "product_name": "PRODUCT_NAME",
                    "category": "CATEGORY",
                    "brand": "BRAND",
                    "price": "PRODUCT_PRICE",
                    "quantity": "QUANTITY",
                    "discount_percent": "DISCOUNT_PERCENT",
                    "line_total": "LINE_TOTAL",
                    "gross_sales": "GROSS_SALES",
                    "net_sales": "NET_SALES",
                    "status": "STATUS",
                    "payment_method": "PAYMENT_METHOD",
                })
                cols = [
                    "ORDER_ID", "ORDER_DATE", "CUSTOMER_ID", "CUSTOMER_NAME", "EMAIL",
                    "CITY", "COUNTRY", "PRODUCT_ID", "PRODUCT_NAME", "CATEGORY", "BRAND",
                    "PRODUCT_PRICE", "QUANTITY", "DISCOUNT_PERCENT", "LINE_TOTAL",
                    "GROSS_SALES", "NET_SALES", "STATUS", "PAYMENT_METHOD",
                ]
                result = result[cols].sort_values("ORDER_DATE", ascending=False)
                if "LIMIT" in query.upper():
                    limit = int(query.upper().split("LIMIT")[-1].strip().split()[0])
                    result = result.head(limit)
                return _normalize_local_columns(result)

            if "FROM DIM_PRODUCTS" in query and "stock" in query.lower() and "FROM FACT_ORDERS" not in query:
                result = products[["product_id", "product_name", "category", "brand", "stock"]].copy()
                result = result.sort_values("stock").rename(columns={
                    "product_id": "PRODUCT_ID",
                    "product_name": "PRODUCT_NAME",
                    "category": "CATEGORY",
                    "brand": "BRAND",
                    "stock": "STOCK",
                })
                if "LIMIT" in query.upper():
                    limit = int(query.upper().split("LIMIT")[-1].strip().split()[0])
                    result = result.head(limit)
                return _normalize_local_columns(result)

            if "signup_date" in query.lower() and "new_customers" in query.lower():
                monthly = (
                    customers.groupby(pd.Grouper(key="signup_date", freq="ME"))
                    .size()
                    .reset_index(name="NEW_CUSTOMERS")
                )
                monthly.columns = ["MONTH", "NEW_CUSTOMERS"]
                return _normalize_local_columns(monthly.sort_values("MONTH"))

            return pd.DataFrame()

    conn = get_snowflake_connection()
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description] if cursor.description else []

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=columns)
    return df


def normalize_filters(filters: dict) -> dict:
    normalized = {
        "start_date": filters.get("start_date"),
        "end_date": filters.get("end_date"),
        "countries": filters.get("countries") or [],
        "categories": filters.get("categories") or [],
        "brands": filters.get("brands") or [],
        "payment_methods": filters.get("payment_methods") or [],
        "statuses": filters.get("statuses") or [],
    }
    if isinstance(normalized["start_date"], str):
        normalized["start_date"] = date.fromisoformat(normalized["start_date"])
    if isinstance(normalized["end_date"], str):
        normalized["end_date"] = date.fromisoformat(normalized["end_date"])
    return normalized


def format_currency(value, currency_symbol="$") -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "-"
    return f"{currency_symbol}{value:,.2f}"


def format_integer(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "-"
    return f"{int(value):,}"
