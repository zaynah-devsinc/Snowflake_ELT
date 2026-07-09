import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "python"))
sys.path.insert(0, str(ROOT_DIR))

import snowflake.connector
import snowflake_config


class TestSnowflakeDataSource(unittest.TestCase):
    def setUp(self) -> None:
        self.config = snowflake_config.load_snowflake_config()
        try:
            self.valid_config = snowflake_config.validate_snowflake_config(self.config)
        except ValueError as exc:
            self.skipTest(f"Snowflake config missing or incomplete: {exc}")

    def _get_connection(self):
        return snowflake.connector.connect(
            **self.valid_config,
            client_session_keep_alive=True,
        )

    def test_fact_orders_has_rows(self):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM FACT_ORDERS")
                result = cursor.fetchone()

        self.assertIsNotNone(result, "Snowflake query returned no result")
        self.assertGreater(result[0], 0, "FACT_ORDERS should contain rows in Snowflake")

    def test_dim_products_stock_column_exists(self):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_NAME = 'DIM_PRODUCTS' "
                    "AND COLUMN_NAME = 'STOCK'"
                )
                result = cursor.fetchone()

        self.assertIsNotNone(result, "Snowflake query returned no result")
        self.assertGreater(result[0], 0, "DIM_PRODUCTS must expose the STOCK column")

    def test_fact_orders_matches_local_raw_data(self):
        items_path = ROOT_DIR / "data" / "raw" / "order_items.csv"

        items = pd.read_csv(items_path)
        local_total_net = items["line_total"].sum()
        local_item_count = len(items)

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT SUM(net_sales) AS total_net, COUNT(*) AS row_count, COUNT(DISTINCT order_item_id) AS distinct_item_count FROM FACT_ORDERS"
                )
                snow_total_net, snow_row_count, snow_distinct_item_count = cursor.fetchone()

        self.assertEqual(
            snow_distinct_item_count,
            local_item_count,
            "Snowflake FACT_ORDERS distinct order_item_id count must match raw order_items line count",
        )
        self.assertEqual(
            snow_row_count,
            snow_distinct_item_count,
            "FACT_ORDERS must not contain duplicate order_item_id values",
        )
        self.assertAlmostEqual(
            float(snow_total_net),
            float(local_total_net),
            places=2,
            msg="Snowflake FACT_ORDERS net sales should match raw order_items net sales",
        )


if __name__ == "__main__":
    unittest.main()
