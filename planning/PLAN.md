# PLAN

## Project: Modern Snowflake ELT Data Warehouse

### Objective
Build a production-style ELT pipeline that ingests raw e-commerce data into Snowflake, transforms it with dbt using a Medallion Architecture, automates incremental processing with Streams and Tasks, and exposes business-ready analytics in Snowsight.

### Tech Stack
| Category | Technology |
|---|---|
| Cloud Data Warehouse | Snowflake |
| Data Transformation | dbt Core |
| Data Generation | Python |
| Source Data | CSV / JSON |
| Version Control | Git & GitHub |
| IDE | VS Code |
| Analytics | Snowsight |
| Automation | Snowflake Streams & Tasks |

### High-Level Architecture

Python
   │
Generate CSV Files
   │
   ▼
RAW Schema
   │
COPY INTO
   ▼
STAGING Schema
(dbt Cleaning & Standardization)
   │
   ▼
MARTS Schema
(Fact & Dimension Tables)
   │
FACT_ORDERS
   │
Linear Regression Model
   │
Revenue Forecast
   │
Forecast Dashboard

### Forecasting Approach
- Aggregate monthly revenue from `FACT_ORDERS`.
- Train a simple linear regression model on sequential month indices.
- Predict the next 3 months of revenue from the learned trend.
- Store outputs in `forecasts/monthly_revenue.csv` and `forecasts/revenue_forecast.csv`.

### Project Structure

```
snowflake-elt-warehouse/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── marts/
│   │   └── intermediate/
│   ├── snapshots/
│   ├── seeds/
│   └── tests/
│
├── sql/
│   ├── 01_setup.sql
│   ├── 02_tables.sql
│   ├── 03_load_data.sql
│   ├── 04_streams.sql
│   ├── 05_tasks.sql
│   └── 06_views.sql
│
├── python/
│   ├── generate_data.py
│   ├── forecast_revenue.py
│   └── utils.py
│
├── forecasts/
│   ├── monthly_revenue.csv
│   └── revenue_forecast.csv
│
├── docs/
├── screenshots/
├── README.md
└── requirements.txt
```

### Data Model
We'll simulate an e-commerce company.

#### Customers
- customer_id
- first_name
- last_name
- email
- phone
- city
- country
- signup_date

#### Products
- product_id
- product_name
- category
- brand
- price
- stock

#### Orders
- order_id
- customer_id
- order_date
- status
- payment_method

#### Order Items
- order_item_id
- order_id
- product_id
- quantity
- unit_price
- discount

### Medallion Architecture

#### RAW
Purpose:
- Store data exactly as received.
- No transformations.

Tables:
- customers
- products
- orders
- order_items

#### STAGING
Purpose:
- Clean data.
- Rename columns.
- Fix data types.
- Remove duplicates.
- Standardize formats.

Tables:
- stg_customers
- stg_products
- stg_orders
- stg_order_items

#### MARTS
Purpose:
- Business-ready analytical model.

Dimensions:
- dim_customers
- dim_products
- dim_date

Facts:
- fact_orders

### Business KPIs
We'll build queries and dashboards for:
- Total Revenue
- Revenue by Month
- Revenue by Country
- Top 10 Customers
- Top 10 Products
- Average Order Value
- Repeat Customer Rate
- Orders by Payment Method
- Customer Lifetime Value (CLV)
- Forecasted Revenue
- Forecast Growth Rate

### Forecast Model and Metrics
- Model: Linear regression on monthly revenue.
- Formula: `revenue = slope * month_index + intercept`.
- Inputs: sequential month index (0, 1, 2, ...) and monthly revenue totals.
- Outputs: next 3 months of predicted revenue.
- Dashboard metrics:
  - Last month revenue
  - Predicted next month revenue
  - Expected growth % vs last actual month
  - Training period
  - Forecast horizon

### dbt Features We'll Use
- Sources
- Models
- ref()
- source()
- Jinja
- CTEs
- Incremental Models
- Tests (unique, not_null, relationships)
- Documentation
- Lineage Graph
- Snapshots (optional enhancement)

### Snowflake Features We'll Use
- Warehouses
- Databases
- Schemas
- Internal Stages
- COPY INTO
- File Formats
- Streams
- Tasks
- Views
- Snowsight Dashboards

### GitHub Deliverables
Your repository will include:
- Well-organized project structure
- SQL scripts
- dbt project
- Python data generator
- Sample datasets
- Architecture diagram
- Screenshots
- Dashboard screenshots
- Comprehensive README with setup instructions

### Project Milestones
#### Phase 1 – Environment Setup ✅
- Snowflake account
- Warehouse
- Database
- Schemas
- Git repository
- VS Code setup

#### Phase 2 – Data Generation
- Create realistic e-commerce datasets
- Export to CSV

#### Phase 3 – Data Ingestion
- Create RAW tables
- Upload files
- Load with COPY INTO

#### Phase 4 – dbt Development
- Initialize dbt
- Configure Snowflake connection
- Build staging models
- Add tests and documentation

#### Phase 5 – Dimensional Modeling
- Create fact and dimension tables
- Build business metrics

#### Phase 6 – Incremental ELT
- Implement incremental dbt models
- Create Streams
- Schedule Tasks

#### Phase 7 – Analytics
- Build Snowsight dashboards
- Create business views
- Add Forecast dashboard page
- Integrate forecast outputs with dashboard metrics

#### Phase 8 – Project Polish
- Improve README
- Add architecture diagrams
- Document forecast model and assumptions
- Capture screenshots
- Push final code to GitHub

### Final Outcome
By the end of this project, you'll have an end-to-end cloud data engineering portfolio project that demonstrates:
- Modern ELT with Snowflake
- Data modeling using the Medallion Architecture
- dbt transformations and testing
- Incremental processing
- Automation with Streams and Tasks
- Business analytics in Snowsight
- Production-style project organization suitable for GitHub and interviews
