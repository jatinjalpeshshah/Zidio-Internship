# Project Foresight

## AI-Powered Demand Forecasting & Inventory Intelligence Dashboard

Project Foresight is an end-to-end retail analytics project that combines:

- Demand forecasting
- Forecast vs actual analysis
- Inventory risk scoring
- Stockout risk detection
- Overstock identification
- Replenishment prioritization
- Business impact analysis
- Interactive Streamlit dashboard

## Dashboard

The final application provides:

1. Executive Overview
2. Sales & Forecast Intelligence
3. Inventory Risk Intelligence
4. Replenishment Priority
5. Overstock / Markdown Intelligence
6. SKU Explorer
7. Category Intelligence

## Dashboard Features

- Global category filtering
- Global risk filtering
- Global inventory status filtering
- SKU search
- Interactive Plotly visualizations
- KPI cards
- Business impact metrics
- Risk analysis
- Replenishment recommendations
- Overstock analysis
- Downloadable CSV data

## Validated Dashboard Data

The dashboard uses four validated datasets:

- `dashboard_sku_summary.csv`
- `dashboard_forecast_actual.csv`
- `dashboard_category_summary.csv`
- `dashboard_kpi_summary.csv`

## Key Project Metrics

- Total SKUs: 5,000
- Forecast Demand: 1,428,009 units
- Actual Units: 1,451,152 units
- Stock on Hand: 452,556 units
- Replenishment Required: 1,063,885 units
- Excess Inventory: 88,432 units
- Overall WAPE: 35.16%
- Critical SKUs: 153
- High-Risk SKUs: 747
- Shortage SKUs: 3,967
- Surplus SKUs: 1,016
- Sales Value at Risk: ₹659,983,337.20
- Capital Locked in Overstock: ₹36,236,959.08

## Validation

The final dashboard data passed:

**39 / 39 validation checks**

The validation covered:

- Schema validation
- SKU master mapping
- Forecast grain
- Forecast values
- Actual sales values
- Inventory arithmetic
- Replenishment arithmetic
- Excess inventory arithmetic
- Inventory status consistency
- Recommended action consistency
- Risk score validation
- Category reconciliation
- KPI reconciliation
- Financial impact validation
- Business sanity checks

## Technology

- Python
- Pandas
- NumPy
- Streamlit
- Plotly

## Deployment

The application is designed for deployment using Streamlit Community Cloud.

The Streamlit entrypoint is:

`app.py`

Dashboard data is stored under:

`data/`

## Project Status

Final dashboard QA completed successfully.

The dashboard is ready for deployment.
