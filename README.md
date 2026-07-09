# SnowflakeELTWarehouse

## Run Pipeline

Use the root helper script to execute the end-to-end pipeline:

```bash
cd /Users/d-23-9386/Desktop/SnowflakeELTWarehouse
source venv/bin/activate
python3 -m pip install -r requirements.txt
chmod +x run_pipeline.sh
./run_pipeline.sh
```

This generates raw CSV data, loads the raw CSVs into Snowflake, installs Python dependencies, runs dbt models and tests, generates dbt docs, and creates revenue forecast files.

### Running the forecast manually

If you need to generate forecast data separately:

```bash
cd /Users/d-23-9386/Desktop/SnowflakeELTWarehouse
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 python/forecast_revenue.py
```

The forecast script requires Snowflake credentials in environment variables:
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE` (default: `ELT_WAREHOUSE`)
- `SNOWFLAKE_SCHEMA` (default: `RAW_MARTS`)
- `SNOWFLAKE_ROLE` (optional)

Forecast outputs are written to `forecasts/revenue_forecast.csv` and `forecasts/monthly_revenue.csv`.

### Full run instructions

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Install requirements:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
3. Run the full project pipeline:
   ```bash
   chmod +x run_pipeline.sh
   ./run_pipeline.sh
   ```
4. Open the Streamlit dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```
5. Visit the Forecast page inside the dashboard after forecast files are generated.

## Running tests

A Snowflake source validation test has been added to `tests/test_snowflake_data_source.py`.

Run it from the repository root after activating your virtual environment:

```bash
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m unittest tests.test_snowflake_data_source
```

This test confirms:
- Snowflake credentials are available
- `FACT_ORDERS` contains rows in Snowflake
- `DIM_PRODUCTS` exposes the `STOCK` column
- Snowflake `FACT_ORDERS` aggregates match the raw CSV source

## Revenue Forecasting

The forecasting feature trains a linear regression model on historical monthly revenue from `RAW_MARTS.FACT_ORDERS` and predicts the next 3 months of revenue.

- Linear Regression is used because it is a simple, interpretable model that fits the project’s historical revenue trend and provides a baseline forecast.
- Training data is built by aggregating monthly revenue from `FACT_ORDERS`.
- Prediction uses a month index (0, 1, 2, ...) and predicts future revenue values.
- Forecast results are written to `forecasts/revenue_forecast.csv` and historical revenue to `forecasts/monthly_revenue.csv`.
- The Streamlit Forecast page reads these files and displays KPI cards, charts, prediction tables, and rule-based insights.

### Updated architecture

CSV Data
↓
Snowflake RAW
↓
dbt Staging
↓
dbt Marts
↓
FACT_ORDERS
↓
Linear Regression Model
↓
Revenue Forecast
↓
Forecast Dashboard

