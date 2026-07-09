#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import snowflake.connector
from snowflake_config import load_snowflake_config, validate_snowflake_config

RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
SQL_DIR = ROOT_DIR / "sql"

SOURCE_FILES = {
    "customers": "customers.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv",
}


def _get_connection():
    config = load_snowflake_config()
    validated = validate_snowflake_config(config)
    connection_args = {
        "user": validated["user"],
        "password": validated["password"],
        "account": validated["account"],
        "warehouse": validated["warehouse"],
        "database": validated["database"],
        "schema": "RAW",
    }
    if validated.get("role"):
        connection_args["role"] = validated["role"]
    return snowflake.connector.connect(**connection_args)


def _execute_sql_script(cursor, script_path: Path):
    sql_text = script_path.read_text()
    for statement in sql_text.split(";"):
        statement = statement.strip()
        if not statement:
            continue
        cursor.execute(statement)


def _load_source_files(cursor):
    config = load_snowflake_config()
    validated = validate_snowflake_config(config)
    database_name = validated["database"]
    cursor.execute(f"USE DATABASE {database_name}")
    cursor.execute("USE SCHEMA RAW")
    print(f"Using database {database_name} and schema RAW")

    for table_name, filename in SOURCE_FILES.items():
        csv_path = RAW_DATA_DIR / filename
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing required raw file: {csv_path}")

        print(f"Uploading {filename} to Snowflake stage...")
        cursor.execute(
            f"PUT file://{csv_path.as_posix()} @raw_stage AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
        )

        print(f"Truncating RAW.{table_name} before load...")
        cursor.execute(f"TRUNCATE TABLE IF EXISTS RAW.{table_name}")

        print(f"Copying {filename} into RAW.{table_name}...")
        cursor.execute(
            f"COPY INTO RAW.{table_name} FROM @raw_stage/{filename}.gz "
            "FILE_FORMAT=(FORMAT_NAME=csv_format) "
            "MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE "
            "ON_ERROR = 'ABORT_STATEMENT'"
        )

        print(f"Loaded {filename} into RAW.{table_name}")


def main():
    print("Starting Snowflake raw data load...")
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            print("Applying Snowflake setup and raw table DDL...")
            _execute_sql_script(cursor, SQL_DIR / "01_setup.sql")
            _execute_sql_script(cursor, SQL_DIR / "02_create_tables.sql")
            _execute_sql_script(cursor, SQL_DIR / "03_load_data.sql")
            _load_source_files(cursor)
            print("Snowflake raw data load complete.")


if __name__ == "__main__":
    main()
