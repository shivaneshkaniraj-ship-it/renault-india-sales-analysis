"""
Renault India — Sales Analysis Pipeline
Consolidated script: load -> clean -> reshape -> EDA -> forecast

Run with: python3 analysis.py
Produces: data/*.csv (derived tables) and charts/*.png
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')

# ============================================================
# STEP 1: LOAD + CLEAN
# ============================================================
df = pd.read_csv('data/Car_data.csv')

# The raw file has 5 metadata columns (Car Name, Brand, Country, Body Style, Segment)
# followed by 180 monthly sales columns (Jan-11 ... Dec-25) — one row per model.
sales_cols = df.columns[5:]

# A handful of models (11 of them, none Renault) have a few missing monthly values.
# We fill with 0 — consistent with the surrounding zero-sales pattern for models
# that hadn't launched yet or had already been discontinued in that window.
df[sales_cols] = df[sales_cols].fillna(0)

# ============================================================
# STEP 2: RESHAPE (wide -> long)
# ============================================================
# Wide format is one row per car with 180 date columns — great for storage,
# unusable for time-series analysis. We melt it into long format:
# one row per (car, month) with a single Sales value. This is the standard
# "tidy data" shape that pandas groupby/plotting expects.
long_df = df.melt(
    id_vars=['Car Name', 'Brand', 'Country of Origin', 'Body Style', 'Segment'],
    var_name='MonthStr',
    value_name='Sales'
)
# Convert 'Jan-11' style strings into real datetime objects so we can sort/plot by time
long_df['Month'] = pd.to_datetime(long_df['MonthStr'], format='%b-%y')
long_df['Sales'] = long_df['Sales'].astype(int)
long_df = long_df.drop(columns=['MonthStr']).sort_values(['Car Name', 'Month']).reset_index(drop=True)
long_df.to_csv('data/car_sales_long.csv', index=False)

# ============================================================
# STEP 3: DERIVED TABLES
# ============================================================
# Total industry sales per month = sum across all 210 models
industry_monthly = long_df.groupby('Month')['Sales'].sum().reset_index()
industry_monthly.columns = ['Month', 'Industry_Total']

# Renault-only sales per month = sum across Renault's 10 models
renault_monthly = long_df[long_df['Brand'] == 'Renault'].groupby('Month')['Sales'].sum().reset_index()
renault_monthly.columns = ['Month', 'Renault_Total']

# Market share = Renault's sales / industry sales, per month
merged = industry_monthly.merge(renault_monthly, on='Month', how='left')
merged['Renault_Total'] = merged['Renault_Total'].fillna(0)
merged['Market_Share_Pct'] = merged['Renault_Total'] / merged['Industry_Total'] * 100
merged.to_csv('data/renault_market_share.csv', index=False)

# Renault sales broken out by model, wide format (useful for the model-mix chart)
renault_wide = df[df['Brand'] == 'Renault'].set_index('Car Name')[sales_cols].T
renault_wide.index = pd.to_datetime(renault_wide.index, format='%b-%y')
renault_wide.to_csv('data/renault_by_model_wide.csv')

# ============================================================
# STEP 4: EDA CHARTS
# ============================================================

# Chart 1 — industry-wide trend, full 15-year history
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(industry_monthly['Month'], industry_monthly['Industry_Total'], color='#1f77b4', linewidth=1.3)
ax.set_title('India Passenger Vehicle Industry — Monthly Sales (2011–2025)', fontsize=13, fontweight='bold')
ax.set_ylabel('Units sold/month')
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.tight_layout()
plt.savefig('charts/01_industry_trend.png', dpi=140)
plt.close()

# Chart 2 — Renault's sales AND market share on one chart (dual y-axis)
# Two different units (units/month vs %) need two separate y-axes sharing one x-axis
fig, ax1 = plt.subplots(figsize=(11, 4.5))
ax1.plot(merged['Month'], merged['Renault_Total'], color='#d62728', linewidth=1.3)
ax1.set_ylabel('Renault units/month', color='#d62728')
ax1.tick_params(axis='y', labelcolor='#d62728')
ax2 = ax1.twinx()  # twinx() creates a second y-axis sharing the same x-axis
ax2.plot(merged['Month'], merged['Market_Share_Pct'], color='#2ca02c', linewidth=1, alpha=0.6)
ax2.set_ylabel('Market share (%)', color='#2ca02c')
ax2.tick_params(axis='y', labelcolor='#2ca02c')
ax1.set_title('Renault India — Monthly Sales & Market Share (2011–2025)', fontsize=13, fontweight='bold')
ax1.xaxis.set_major_locator(mdates.YearLocator(2))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.tight_layout()
plt.savefig('charts/02_renault_sales_share.png', dpi=140)
plt.close()

# Chart 3 — model mix, stacked area, last 3 years only (recent lineup is what matters)
renault_wide_recent = renault_wide[renault_wide.index >= '2023-01-01']
renault_wide_recent = renault_wide_recent.loc[:, (renault_wide_recent.sum() > 0)]  # drop dead models
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.stackplot(renault_wide_recent.index,
             [renault_wide_recent[c] for c in renault_wide_recent.columns],
             labels=renault_wide_recent.columns, alpha=0.85)
ax.set_title('Renault India — Model Mix, Last 3 Years (2023–2025)', fontsize=13, fontweight='bold')
ax.set_ylabel('Units/month')
ax.legend(loc='upper left', fontsize=9)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('charts/03_renault_model_mix.png', dpi=140)
plt.close()

# ============================================================
# STEP 5: COMPETITIVE BENCHMARKING (2025 snapshot)
# ============================================================
df_2025 = long_df[long_df['Month'].dt.year == 2025]
brand_totals_2025 = df_2025.groupby('Brand')['Sales'].sum().sort_values(ascending=False)
total_2025 = brand_totals_2025.sum()
renault_rank = list(brand_totals_2025.index).index('Renault') + 1
print(f"Renault 2025 rank: #{renault_rank} of {len(brand_totals_2025)} brands, "
      f"{brand_totals_2025['Renault']:,} units ({brand_totals_2025['Renault']/total_2025*100:.2f}% share)")

# ============================================================
# STEP 6: FORECASTING (SARIMA)
# ============================================================
# Why SARIMA: it's Seasonal ARIMA — handles both a trend AND a repeating
# yearly pattern (e.g. festive-season spikes in Oct/Nov), which plain
# regression or a moving average would miss.
#
# Why 2019 onward only: Renault's older models (Fluence, Koleos, Pulse,
# Scala, Lodgy) were discontinued years ago. Training on the full
# 2011-2025 history would blend two unrelated product eras into one
# series and produce a meaningless trend line.
renault_series = merged.set_index('Month')['Renault_Total']
renault_series.index.freq = 'MS'  # 'MS' = Month Start frequency
series_recent = renault_series[renault_series.index >= '2019-01-01']

# --- Validation: hide the last 6 real months, see if the model predicts them ---
train = series_recent[:-6]
test = series_recent[-6:]

# order=(p,d,q): p=autoregressive terms, d=differencing (removes trend), q=moving-average terms
# seasonal_order=(P,D,Q,s): same idea but for the yearly (s=12) seasonal pattern
model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 0, 12),
                 enforce_stationarity=False, enforce_invertibility=False)
fit = model.fit(disp=False)
pred_test = fit.get_forecast(steps=6).predicted_mean
mape = (np.abs((test.values - pred_test.values) / test.values)).mean() * 100
print(f"Validation MAPE (last 6 known months): {mape:.1f}%")

# --- Refit on ALL available data, forecast 6 months into the future ---
final_model = SARIMAX(series_recent, order=(1, 1, 1), seasonal_order=(1, 1, 0, 12),
                       enforce_stationarity=False, enforce_invertibility=False)
final_fit = final_model.fit(disp=False)
fc = final_fit.get_forecast(steps=6)
future_ci = fc.conf_int(alpha=0.2)  # alpha=0.2 -> 80% confidence interval

forecast_df = pd.DataFrame({
    'Forecast': fc.predicted_mean.round(0).astype(int),
    'Lower_80CI': future_ci.iloc[:, 0].round(0).astype(int).clip(lower=0),
    'Upper_80CI': future_ci.iloc[:, 1].round(0).astype(int)
})
forecast_df.index.name = 'Month'
forecast_df.to_csv('data/renault_forecast_next6.csv')

# Chart 4 — forecast with confidence band
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(series_recent.index, series_recent.values, color='#1f77b4', label='Actual (2019–2025)', linewidth=1.3)
ax.plot(forecast_df.index, forecast_df['Forecast'], color='#d62728', linestyle='--',
        marker='o', markersize=4, label='Forecast (next 6 months)')
ax.fill_between(forecast_df.index, forecast_df['Lower_80CI'], forecast_df['Upper_80CI'],
                 color='#d62728', alpha=0.15, label='80% confidence interval')
ax.set_title('Renault India — Monthly Sales Forecast (SARIMA)', fontsize=13, fontweight='bold')
ax.set_ylabel('Units/month')
ax.legend(loc='upper left', fontsize=9)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.tight_layout()
plt.savefig('charts/04_renault_forecast.png', dpi=140)
plt.close()

print("\nDone. Charts in charts/, derived tables in data/.")

# ============================================================
# STEP 7: BRAND COMPARISON — Renault vs Tata, Toyota, Hyundai
# ============================================================
COMPARE_BRANDS = ['Renault', 'Tata', 'Toyota', 'Hyundai']
COLORS = {'Renault': '#d62728', 'Tata': '#1f77b4', 'Toyota': '#2ca02c', 'Hyundai': '#9467bd'}

# Monthly sales + market share per brand, side by side
brand_monthly = long_df[long_df['Brand'].isin(COMPARE_BRANDS)].groupby(['Brand', 'Month'])['Sales'].sum().reset_index()
brand_pivot = brand_monthly.pivot(index='Month', columns='Brand', values='Sales').fillna(0)
brand_pivot = brand_pivot.merge(industry_monthly.set_index('Month'), left_index=True, right_index=True)
for b in COMPARE_BRANDS:
    brand_pivot[f'{b}_share_pct'] = brand_pivot[b] / brand_pivot['Industry_Total'] * 100
brand_pivot.to_csv('data/brand_comparison_monthly.csv')

# 2025 snapshot: total sales + market share per brand
df_2025 = long_df[(long_df['Month'].dt.year == 2025) & (long_df['Brand'].isin(COMPARE_BRANDS))]
total_2025 = long_df[long_df['Month'].dt.year == 2025]['Sales'].sum()
snapshot = df_2025.groupby('Brand')['Sales'].sum().reindex(COMPARE_BRANDS)
snapshot_df = pd.DataFrame({
    'Brand': COMPARE_BRANDS,
    'Sales_2025': snapshot.values,
    'Market_Share_2025_Pct': (snapshot.values / total_2025 * 100).round(2)
})
snapshot_df.to_csv('data/brand_2025_snapshot.csv', index=False)

# Top-selling models per brand, 2025
rows = []
for b in COMPARE_BRANDS:
    m = df_2025[df_2025['Brand'] == b].groupby('Car Name')['Sales'].sum().sort_values(ascending=False)
    m = m[m > 0]
    for model, sales in m.items():
        rows.append({'Brand': b, 'Model': model, 'Sales_2025': sales})
pd.DataFrame(rows).to_csv('data/brand_top_models_2025.csv', index=False)

# Chart 5 — multi-brand sales trend, last 3 years
recent = brand_pivot[brand_pivot.index >= '2023-01-01']
fig, ax = plt.subplots(figsize=(11, 5))
for b in COMPARE_BRANDS:
    ax.plot(recent.index, recent[b], label=b, color=COLORS[b], linewidth=1.5)
ax.set_title('Monthly Sales — Renault vs Tata, Toyota, Hyundai (2023–2025)', fontsize=13, fontweight='bold')
ax.set_ylabel('Units/month')
ax.legend(loc='upper left', fontsize=9)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('charts/05_brand_sales_comparison.png', dpi=140)
plt.close()

# Chart 6 — multi-brand market share trend, last 3 years
fig, ax = plt.subplots(figsize=(11, 5))
for b in COMPARE_BRANDS:
    ax.plot(recent.index, recent[f'{b}_share_pct'], label=b, color=COLORS[b], linewidth=1.5)
ax.set_title('Market Share — Renault vs Tata, Toyota, Hyundai (2023–2025)', fontsize=13, fontweight='bold')
ax.set_ylabel('Market share (%)')
ax.legend(loc='upper left', fontsize=9)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('charts/06_brand_share_comparison.png', dpi=140)
plt.close()

# Chart 7 — top-selling models per brand, 2025 (2x2 grid)
top_models = pd.read_csv('data/brand_top_models_2025.csv')
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for ax, b in zip(axes.flat, COMPARE_BRANDS):
    d = top_models[top_models['Brand'] == b].sort_values('Sales_2025', ascending=True).tail(6)
    ax.barh(d['Model'], d['Sales_2025'], color=COLORS[b])
    ax.set_title(f'{b} — Top models, 2025', fontsize=11, fontweight='bold')
    ax.set_xlabel('Units sold, 2025')
plt.tight_layout()
plt.savefig('charts/07_top_models_by_brand.png', dpi=140)
plt.close()

print("Brand comparison: charts 5-7 saved, snapshot below.")
print(snapshot_df)

# ============================================================
# STEP 8: MARKET SHARE PIE CHART (2025, vs rest of market)
# ============================================================
COLORS_PIE = dict(COLORS, **{'Rest of market': '#c7c7c7'})
industry_total_2025 = long_df[long_df['Month'].dt.year == 2025]['Sales'].sum()
rest = industry_total_2025 - snapshot_df['Sales_2025'].sum()
labels = list(snapshot_df['Brand']) + ['Rest of market']
sizes = list(snapshot_df['Sales_2025']) + [rest]
pie_colors = [COLORS_PIE[b] for b in labels]

fig, ax = plt.subplots(figsize=(7, 7))
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=pie_colors,
                                    startangle=90, pctdistance=0.8,
                                    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
for t in autotexts:
    t.set_fontsize(10)
    t.set_color('white')
ax.set_title('2025 Market Share — Renault, Tata, Toyota, Hyundai vs Rest of Market', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/08_market_share_pie_2025.png', dpi=140)
plt.close()

# ============================================================
# STEP 9: FORECAST ALL BRANDS (SARIMA, same method as Renault)
# ============================================================
all_forecasts, all_validation = [], []
for b in COMPARE_BRANDS:
    b_series = brand_pivot[b][brand_pivot.index >= '2019-01-01']
    b_train, b_test = b_series[:-6], b_series[-6:]
    m = SARIMAX(b_train, order=(1, 1, 1), seasonal_order=(1, 1, 0, 12),
                enforce_stationarity=False, enforce_invertibility=False)
    f = m.fit(disp=False)
    pred = f.get_forecast(steps=6).predicted_mean
    denom = np.where(b_test.values == 0, np.nan, b_test.values)
    mape_b = (np.abs((b_test.values - pred.values) / denom)).mean() * 100
    all_validation.append({'Brand': b, 'Validation_MAPE_Pct': round(mape_b, 1)})

    final_m = SARIMAX(b_series, order=(1, 1, 1), seasonal_order=(1, 1, 0, 12),
                       enforce_stationarity=False, enforce_invertibility=False)
    final_f = final_m.fit(disp=False)
    fc_b = final_f.get_forecast(steps=6)
    ci_b = fc_b.conf_int(alpha=0.2)
    fdf = pd.DataFrame({
        'Brand': b,
        'Forecast': fc_b.predicted_mean.round(0).astype(int),
        'Lower_80CI': ci_b.iloc[:, 0].round(0).astype(int).clip(lower=0),
        'Upper_80CI': ci_b.iloc[:, 1].round(0).astype(int)
    })
    fdf.index.name = 'Month'
    all_forecasts.append(fdf.reset_index())

forecast_all_brands = pd.concat(all_forecasts, ignore_index=True)
forecast_all_brands.to_csv('data/all_brands_forecast_next6.csv', index=False)
pd.DataFrame(all_validation).to_csv('data/all_brands_forecast_validation.csv', index=False)
print("\nAll-brand forecast validation (lower = more reliable):")
print(pd.DataFrame(all_validation))

# Chart 9 — forecast comparison, 2x2 grid
fig, axes = plt.subplots(2, 2, figsize=(13, 8))
for ax, b in zip(axes.flat, COMPARE_BRANDS):
    hist = brand_pivot[b][brand_pivot.index >= '2024-01-01']
    fc = forecast_all_brands[forecast_all_brands['Brand'] == b].set_index('Month')
    ax.plot(hist.index, hist.values, color=COLORS[b], label='Actual')
    ax.plot(fc.index, fc['Forecast'], color=COLORS[b], linestyle='--', marker='o', markersize=3, label='Forecast')
    ax.fill_between(fc.index, fc['Lower_80CI'], fc['Upper_80CI'], color=COLORS[b], alpha=0.15)
    ax.set_title(b, fontsize=11, fontweight='bold')
    ax.legend(fontsize=8)
plt.suptitle('6-Month Forecast — All Brands (SARIMA)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/09_all_brands_forecast.png', dpi=140)
plt.close()
print("\nCharts 8-9 saved.")
