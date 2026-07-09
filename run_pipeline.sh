#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD=python3

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

echo "\n=== Snowflake ELT Warehouse Run Pipeline ===\n"

if ! command_exists "$PYTHON_CMD"; then
  echo "ERROR: Python 3 is required but not found. Install Python 3 and try again."
  exit 1
fi

if ! command_exists dbt; then
  echo "ERROR: dbt is required but not installed. Install dbt and try again."
  exit 1
fi

if [ ! -f "$ROOT_DIR/requirements.txt" ]; then
  echo "WARNING: requirements.txt not found at $ROOT_DIR. Skipping Python dependency check."
else
  echo "Installing Python dependencies from requirements.txt..."
  "$PYTHON_CMD" -m pip install -r "$ROOT_DIR/requirements.txt"
fi

echo "\nStep 1: Generating raw datasets..."
"$PYTHON_CMD" "$ROOT_DIR/python/generate_data.py"

echo "\nStep 2: Loading raw CSV data into Snowflake..."
"$PYTHON_CMD" "$ROOT_DIR/python/load_raw_to_snowflake.py"

if [ ! -d "$ROOT_DIR/snowflake_elt" ]; then
  echo "ERROR: Snowflake dbt project directory 'snowflake_elt' not found."
  exit 1
fi

cd "$ROOT_DIR/snowflake_elt"

echo "\nStep 3: Installing dbt dependencies..."
dbt deps

echo "\nStep 4: Running dbt models..."
dbt run

echo "\nStep 5: Running dbt tests..."
dbt test

echo "\nStep 6: Generating dbt docs..."
dbt docs generate

echo "\nStep 7: Generating revenue forecast..."
"$PYTHON_CMD" "$ROOT_DIR/python/forecast_revenue.py"

cd "$ROOT_DIR"

echo "\nPipeline complete!"
echo "- Raw CSV files: $ROOT_DIR/data/raw/"
echo "- dbt target artifacts: $ROOT_DIR/snowflake_elt/target/"
echo "- dbt docs site available in snowflake_elt/target/"

cat <<'SUMMARY'

Next steps:
- If you want to deploy the SQL ingestion and automation layer, run the SQL scripts in `sql/` against your Snowflake environment.
- Launch the dashboard separately with `streamlit run dashboard/app.py`.

SUMMARY
