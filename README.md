# Renault India — Sales Performance & Market Trend Analysis

An analyst-style case study using 15 years of Indian automotive sales data (2011–2025) to benchmark Renault India's market position, analyze its model mix, and build a short-term sales forecast.

📄 **[Read the full case study](case_study.md)**

## What's in this project

- `data/Car_data.csv` — raw source data (210 models, 19 brands, Jan 2011–Dec 2025)
- `data/car_sales_long.csv` — cleaned, reshaped long-format data used for analysis
- `data/renault_market_share.csv`, `data/renault_by_model_wide.csv`, `data/renault_forecast_next6.csv` — derived tables
- `charts/` — static EDA and forecast charts (PNG)
- `dashboard.py` — interactive Streamlit dashboard
- `case_study.md` — full write-up: problem, method, findings, recommendation

## Key result

Renault India's market share fell from ~3.4% (2020) to 0.83% (2025) even as the industry grew — but the last 2 months of data show a genuine turnaround (+21%, +30% YoY), likely driven by the GST 2.0 rate cut and the Kiger/Triber refresh cycle. Full details in the case study.

**2025 competitive snapshot:** Renault (0.83% share) sits well behind Tata (12.68%) and Hyundai (12.53%), and behind Toyota (7.70%) too. The dashboard's Brand Comparison section breaks this down month by month, plus each brand's top-selling models — Tata's Nexon, Toyota's Innova, and Hyundai's Creta are each their brand's clear #1, versus Renault's Triber.

## Running the dashboard

```bash
pip install streamlit plotly pandas
streamlit run dashboard.py
```

## Tools

Python, pandas, statsmodels (SARIMA), Streamlit, Plotly, matplotlib.

## Data source

Monthly car sales data sourced from Auto Punditz via Kaggle. Select recent data points (Oct 2025–May 2026) cross-referenced against Renault India and SIAM official press releases.
