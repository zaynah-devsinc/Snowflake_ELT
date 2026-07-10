#!/usr/bin/env python3
import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import snowflake.connector
from snowflake_config import load_snowflake_config, has_snowflake_config, validate_snowflake_config

FORECAST_DIR = ROOT_DIR / "forecasts"
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
FORECAST_DIR.mkdir(parents=True, exist_ok=True)


def _load_snowflake_config() -> dict:
    return load_snowflake_config()


def _has_snowflake_config(config: dict) -> bool:
    return has_snowflake_config(config)


def _validate_config(config: dict) -> dict:
    return validate_snowflake_config(config)


def _get_connection(config: dict):
    config = _validate_config(config)
    connection_kwargs = {
        "user": config["user"],
        "password": config["password"],
        "account": config["account"],
        "warehouse": config["warehouse"],
        "database": config["database"],
        "schema": config["schema"],
    }
    if config.get("role"):
        connection_kwargs["role"] = config["role"]
    return snowflake.connector.connect(**connection_kwargs)


def _load_monthly_revenue_snowflake(config: dict) -> pd.DataFrame:
    query = """
SELECT
    sales_month AS month,
    net_revenue AS revenue
FROM SALES_SUMMARY
ORDER BY sales_month
"""
    with _get_connection(config).cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    df["MONTH"] = pd.to_datetime(df["MONTH"])
    return df


def _load_monthly_revenue_local() -> pd.DataFrame:
    orders_path = RAW_DATA_DIR / "orders.csv"
    items_path = RAW_DATA_DIR / "order_items.csv"
    if not orders_path.exists() or not items_path.exists():
        raise FileNotFoundError(
            "Local raw data files are missing. Run python/generate_data.py or set Snowflake credentials."
        )

    orders_df = pd.read_csv(orders_path, parse_dates=["order_date"])
    items_df = pd.read_csv(items_path)

    merged = items_df.merge(
        orders_df[["order_id", "order_date"]],
        on="order_id",
        how="inner",
    )
    merged["order_date"] = pd.to_datetime(merged["order_date"])
    history_df = (
        merged
        .groupby(pd.Grouper(key="order_date", freq="MS"), as_index=False)
        ["line_total"]
        .sum()
        .rename(columns={"order_date": "MONTH", "line_total": "REVENUE"})
    )

    if history_df.empty:
        raise ValueError("No historical revenue found in local raw data.")

    return history_df


def _load_monthly_revenue() -> pd.DataFrame:
    config = _load_snowflake_config()
    if _has_snowflake_config(config):
        return _load_monthly_revenue_snowflake(config)

    print("Snowflake credentials not detected. Using local raw CSV fallback for revenue history.")
    return _load_monthly_revenue_local()


def _create_month_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("MONTH").reset_index(drop=True)
    df["month_index"] = range(len(df))
    return df


def _train_model(df: pd.DataFrame):
    if len(df) < 2:
        raise ValueError("Not enough historical revenue points to train a forecast model.")

    X = df["month_index"].astype(float).values
    y = df["REVENUE"].astype(float).values
    slope, intercept = np.polyfit(X, y, 1)
    return {"slope": float(slope), "intercept": float(intercept)}


def _forecast(model, last_index: int, periods: int) -> pd.DataFrame:
    future_indexes = np.arange(last_index + 1, last_index + 1 + periods, dtype=float)
    predictions = model["slope"] * future_indexes + model["intercept"]
    return pd.DataFrame({"month_index": future_indexes.astype(int), "predicted_revenue": predictions})


def _create_forecast_dates(history_df: pd.DataFrame, forecast_df: pd.DataFrame) -> pd.DataFrame:
    last_month = history_df["MONTH"].max()
    forecast_dates = []
    for offset in range(1, len(forecast_df) + 1):
        year = last_month.year + ((last_month.month - 1 + offset) // 12)
        month = ((last_month.month - 1 + offset) % 12) + 1
        forecast_dates.append(datetime(year, month, 1))
    forecast_df["MONTH"] = forecast_dates
    return forecast_df


def save_forecasts():
    history_df = _load_monthly_revenue()
    history_df = _create_month_index(history_df)

    model = _train_model(history_df)
    print(f"Model slope: {model['slope']:.6f}")
    print(f"Model intercept: {model['intercept']:.6f}")

    forecast_df = _forecast(model, history_df["month_index"].max(), 3)
    forecast_df = _create_forecast_dates(history_df, forecast_df)
    forecast_df = forecast_df[["MONTH", "predicted_revenue"]]
    forecast_df.to_csv(FORECAST_DIR / "revenue_forecast.csv", index=False)

    history_df["revenue"] = history_df["REVENUE"]
    history_df[["MONTH", "revenue"]].to_csv(FORECAST_DIR / "monthly_revenue.csv", index=False)

    print("Saved forecasts/revenue_forecast.csv")
    print("Saved forecasts/monthly_revenue.csv")
    print("Predicted values:")
    print(forecast_df.to_string(index=False))


def main():
    save_forecasts()


if __name__ == "__main__":
    main()
