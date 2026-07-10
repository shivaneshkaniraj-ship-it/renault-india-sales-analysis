# Renault India — Sales Performance & Market Trend Analysis
### An analyst case study | July 2026

---

## 1. Problem

Renault India's market position has visibly shifted over the past decade, but how much, and why? This project analyzes 15 years of monthly car sales data (2011–2025) across 210 models and 19 brands sold in India to quantify Renault's trajectory, benchmark it against the industry and key competitors, and build a short-term sales forecast.

## 2. Data

- **Source:** Monthly car sales by model in India, Jan 2011 – Dec 2025 (180 months), covering 210 models across 19 brands, sourced from Auto Punditz via Kaggle.
- **Fields:** Car name, brand, country of origin, body style, segment, and monthly unit sales.
- **Cleaning:** 11 models had a handful of missing monthly values (max 2 months each, none belonging to Renault); filled with 0, consistent with the surrounding sales pattern (model not yet launched / already discontinued in that window).
- **Reshaping:** Converted from wide (185 columns) to long format for time-series analysis; built derived tables for industry totals, Renault totals, market share, and model-level breakdowns.

## 3. Method

1. **EDA** — industry-wide monthly sales trend (2011–2025), Renault's monthly sales and market share over the same period, and Renault's model mix over the last 3 years.
2. **Competitive benchmarking** — 2025 brand rankings, Renault's segment-level share of the Indian market.
3. **Forecasting** — SARIMA(1,1,1)(1,1,0,12) fitted on Renault's 2019–2025 monthly sales (post-legacy-model era, since Fluence/Koleos/Pulse/Scala/Lodgy are discontinued and blending them with the current Triber/Kiger/Kwid lineup would distort the trend). Validated on the last 6 known months before forecasting 6 months forward.

## 4. Key Findings

**Renault's market share has fallen sharply, even as the industry grew.**
- India's PV industry grew 6.2% in 2025 (4.30M → 4.56M units).
- Renault's sales *declined* 8.8% over the same period (41,729 → 38,065 units).
- Renault's market share dropped from ~3.4% (2020 average) to 0.83% (2025 average) — a peak-to-trough erosion of roughly 4x.
- In 2025, Renault ranked **#11 of 19 brands** in India, behind Maruti Suzuki (39.9% share), Mahindra, Tata, Hyundai, Toyota, and Kia.

**The brand is now a one-model story.**
- Triber alone accounted for **59.9%** of Renault's 2025 volume; Kiger 25.0%; Kwid 15.1%.
- Renault holds close to zero presence in the compact-sedan/hatchback segments (B2, C1, C2, D1, D2) that make up the bulk of India's market — its only real footholds are the Utility/MPV segment (3.2% share, via Triber) and the entry hatchback segment A (4.9% share, via Kwid).

**But the most recent months show a genuine turnaround signal.**
- October 2025: +21% YoY; November 2025: +30% YoY — both outpacing industry growth.
- This coincides with the GST 2.0 rate cut (effective Sept 22, 2025) and renewed momentum on Kiger/Triber.
- The Duster's re-launch (March 2026, ~1,400 units in its first month) adds a new growth lever outside the existing three-model lineup — not yet reflected in the main 2011–2025 dataset, but confirmed via Renault's own press releases.

**Forecast comes with an honest caveat.**
- A SARIMA model trained on 2019–2025 data produced a 6-month-ahead forecast, but validation MAPE on the last 6 known months was **~61%** — the model significantly underpredicted the Sep–Oct 2025 surge.
- This is itself a useful finding: a purely statistical model, trained on historical seasonality, cannot anticipate a policy shock (GST cut) or a launch-driven demand spike. In practice, this kind of forecast needs to be blended with qualitative context — upcoming launches, policy calendar, competitor actions — not used as a standalone number.

## 5. Business Recommendation

Renault India's growth over the next 12–18 months is likely to be **model-cycle-driven rather than trend-driven**: the recent uptick is explained by GST-driven affordability plus the Kiger/Triber refresh cycle, and the Duster's return is a further lever. A forecasting approach that layers a qualitative launch/policy calendar on top of the statistical baseline would give a more decision-useful number than the SARIMA output alone. Given the brand's near-total absence from the high-volume C1/C2 compact segments, the Duster's segment (C2, midsize SUV) re-entry is strategically the highest-leverage move in the current lineup — worth tracking closely in the next 2–3 quarters of data.

## 6. Tools Used

Python (pandas, statsmodels for SARIMA), Streamlit + Plotly for the interactive dashboard, matplotlib for static charts.

---
*Data current through December 2025 for the core dataset; select data points from Renault India and SIAM press releases used for context through May 2026.*
