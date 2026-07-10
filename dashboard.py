"""
Renault India — Sales Performance & Market Trend Dashboard
Run with: streamlit run dashboard.py
"""
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Renault India Sales Analysis", layout="wide")

# ---------- Load data ----------
@st.cache_data
def load_data():
    long_df = pd.read_csv('data/car_sales_long.csv', parse_dates=['Month'])
    share_df = pd.read_csv('data/renault_market_share.csv', parse_dates=['Month'])
    renault_wide = pd.read_csv('data/renault_by_model_wide.csv', index_col=0, parse_dates=True)
    forecast_df = pd.read_csv('data/renault_forecast_next6.csv', parse_dates=['Month'], index_col='Month')
    return long_df, share_df, renault_wide, forecast_df

long_df, share_df, renault_wide, forecast_df = load_data()

st.title("🚗 Renault India — Sales Performance & Market Trend Dashboard")
st.caption("Data: Monthly car sales by model in India, Jan 2011 – Dec 2025 (Kaggle / Auto Punditz)")

# ---------- Top KPIs ----------
latest_month = share_df['Month'].max()
latest_row = share_df[share_df['Month'] == latest_month].iloc[0]
prev_year_row = share_df[share_df['Month'] == latest_month - pd.DateOffset(years=1)]
yoy = None
if not prev_year_row.empty and prev_year_row.iloc[0]['Renault_Total'] > 0:
    yoy = (latest_row['Renault_Total'] - prev_year_row.iloc[0]['Renault_Total']) / prev_year_row.iloc[0]['Renault_Total'] * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest Month", latest_month.strftime('%b %Y'))
col2.metric("Renault Sales", f"{int(latest_row['Renault_Total']):,} units", f"{yoy:.1f}% YoY" if yoy is not None else None)
col3.metric("Market Share", f"{latest_row['Market_Share_Pct']:.2f}%")
col4.metric("Industry Total", f"{int(latest_row['Industry_Total']):,} units")

st.divider()

# ---------- Sales & Market Share over time ----------
st.subheader("Renault Sales & Market Share Over Time")
year_range = st.slider("Select year range", 2011, 2025, (2019, 2025))
filtered = share_df[(share_df['Month'].dt.year >= year_range[0]) & (share_df['Month'].dt.year <= year_range[1])]

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=filtered['Month'], y=filtered['Renault_Total'], name='Renault monthly sales',
                          line=dict(color='#d62728')), secondary_y=False)
fig.add_trace(go.Scatter(x=filtered['Month'], y=filtered['Market_Share_Pct'], name='Market share %',
                          line=dict(color='#2ca02c', dash='dot')), secondary_y=True)
fig.update_yaxes(title_text="Units/month", secondary_y=False)
fig.update_yaxes(title_text="Market share (%)", secondary_y=True)
fig.update_layout(height=420, hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------- Model mix ----------
st.subheader("Model Mix Over Time")
models_available = [c for c in renault_wide.columns if renault_wide[c].sum() > 0]
selected_models = st.multiselect("Select models", models_available, default=models_available)
mix_range = renault_wide[renault_wide.index.year >= 2019]

fig2 = go.Figure()
for m in selected_models:
    fig2.add_trace(go.Scatter(x=mix_range.index, y=mix_range[m], name=m, stackgroup='one'))
fig2.update_layout(height=420, yaxis_title="Units/month", hovermode='x unified')
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------- Forecast ----------
st.subheader("Next 6-Month Forecast (SARIMA)")
st.warning(
    "⚠️ Model validation MAPE on the last 6 known months was ~61% — the model underpredicted "
    "the Sep–Oct 2025 surge driven by GST 2.0 rate cuts and new Kiger/Triber momentum. "
    "This is a real limitation worth stating out loud: statistical models trained on historical "
    "patterns can't anticipate policy shocks or launch-driven demand spikes. Treat the forecast "
    "band as a baseline, not a guarantee.",
    icon="⚠️"
)
recent_actual = share_df[share_df['Month'] >= '2023-01-01'][['Month','Renault_Total']].set_index('Month')

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=recent_actual.index, y=recent_actual['Renault_Total'], name='Actual', line=dict(color='#1f77b4')))
fig3.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['Forecast'], name='Forecast', line=dict(color='#d62728', dash='dash')))
fig3.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['Upper_80CI'], line=dict(width=0), showlegend=False))
fig3.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['Lower_80CI'], line=dict(width=0), fill='tonexty',
                           fillcolor='rgba(214,39,40,0.15)', name='80% confidence interval'))
fig3.update_layout(height=420, yaxis_title="Units/month", hovermode='x unified')
st.plotly_chart(fig3, use_container_width=True)

st.dataframe(forecast_df, use_container_width=True)

st.divider()
st.caption("Built as an analyst-style case study: EDA → market share benchmarking → SARIMA forecasting → business insights.")

# ============================================================
# BRAND COMPARISON — Renault vs Tata, Toyota, Hyundai
# ============================================================
st.divider()
st.header("🆚 Brand Comparison — Renault vs Tata, Toyota, Hyundai")

COMPARE_BRANDS = ['Renault', 'Tata', 'Toyota', 'Hyundai']
BRAND_COLORS = {'Renault': '#d62728', 'Tata': '#1f77b4', 'Toyota': '#2ca02c', 'Hyundai': '#9467bd'}

@st.cache_data
def load_comparison_data():
    comp = pd.read_csv('data/brand_comparison_monthly.csv', parse_dates=['Month'], index_col='Month')
    snapshot = pd.read_csv('data/brand_2025_snapshot.csv')
    top_models = pd.read_csv('data/brand_top_models_2025.csv')
    return comp, snapshot, top_models

comp, snapshot, top_models = load_comparison_data()

# 2025 snapshot KPI cards
cols = st.columns(4)
for i, b in enumerate(COMPARE_BRANDS):
    row = snapshot[snapshot['Brand'] == b].iloc[0]
    cols[i].metric(b, f"{int(row['Sales_2025']):,} units", f"{row['Market_Share_2025_Pct']:.2f}% share")

selected_brands = st.multiselect("Select brands to compare", COMPARE_BRANDS, default=COMPARE_BRANDS)
comp_recent = comp[comp.index >= '2022-01-01']

# Sales trend comparison
st.subheader("Monthly Sales Trend")
fig4 = go.Figure()
for b in selected_brands:
    fig4.add_trace(go.Scatter(x=comp_recent.index, y=comp_recent[b], name=b,
                               line=dict(color=BRAND_COLORS[b])))
fig4.update_layout(height=400, yaxis_title="Units/month", hovermode='x unified')
st.plotly_chart(fig4, use_container_width=True)

# Market share trend comparison (separate chart — different unit than sales)
st.subheader("Market Share Trend")
fig5 = go.Figure()
for b in selected_brands:
    fig5.add_trace(go.Scatter(x=comp_recent.index, y=comp_recent[f'{b}_share_pct'], name=b,
                               line=dict(color=BRAND_COLORS[b])))
fig5.update_layout(height=400, yaxis_title="Market share (%)", hovermode='x unified')
st.plotly_chart(fig5, use_container_width=True)

# Market share as a share breakdown (pie), 2025 snapshot
st.subheader("2025 Market Share Breakdown")
industry_2025_total = 4563015  # computed from full 210-model dataset for 2025
rest_of_market = industry_2025_total - snapshot['Sales_2025'].sum()
pie_labels = list(snapshot['Brand']) + ['Rest of market']
pie_values = list(snapshot['Sales_2025']) + [rest_of_market]
pie_colors = [BRAND_COLORS[b] for b in snapshot['Brand']] + ['#c7c7c7']
fig_pie = go.Figure(go.Pie(labels=pie_labels, values=pie_values, marker=dict(colors=pie_colors),
                            textinfo='label+percent', hole=0.4))
fig_pie.update_layout(height=450)
st.plotly_chart(fig_pie, use_container_width=True)

# Top-selling models per brand, 2025
st.subheader("Top-Selling Models by Brand, 2025")
tab_objs = st.tabs(selected_brands)
for tab, b in zip(tab_objs, selected_brands):
    with tab:
        d = top_models[top_models['Brand'] == b].sort_values('Sales_2025', ascending=True)
        fig6 = go.Figure(go.Bar(x=d['Sales_2025'], y=d['Model'], orientation='h',
                                 marker_color=BRAND_COLORS[b]))
        fig6.update_layout(height=300, xaxis_title="Units sold, 2025")
        st.plotly_chart(fig6, use_container_width=True)

# Forecast comparison — all 4 brands
st.subheader("6-Month Forecast — All Brands")
@st.cache_data
def load_all_forecasts():
    fc = pd.read_csv('data/all_brands_forecast_next6.csv', parse_dates=['Month'])
    val = pd.read_csv('data/all_brands_forecast_validation.csv')
    return fc, val

forecast_all, validation_all = load_all_forecasts()

val_cols = st.columns(4)
for i, row in validation_all.iterrows():
    val_cols[i].metric(f"{row['Brand']} validation error", f"{row['Validation_MAPE_Pct']}%")
st.caption("Lower validation error (MAPE) means the forecast is more reliable. Renault's error is "
           "high because it's a small, volatile brand — Hyundai/Toyota's larger, steadier volumes "
           "are structurally easier to forecast. This gap is itself a real finding, not noise.")

forecast_brand_tabs = st.tabs(selected_brands)
for tab, b in zip(forecast_brand_tabs, selected_brands):
    with tab:
        hist = comp[b][comp.index >= '2024-01-01']
        fc_b = forecast_all[forecast_all['Brand'] == b].set_index('Month')
        fig7 = go.Figure()
        fig7.add_trace(go.Scatter(x=hist.index, y=hist.values, name='Actual', line=dict(color=BRAND_COLORS[b])))
        fig7.add_trace(go.Scatter(x=fc_b.index, y=fc_b['Forecast'], name='Forecast',
                                   line=dict(color=BRAND_COLORS[b], dash='dash')))
        fig7.add_trace(go.Scatter(x=fc_b.index, y=fc_b['Upper_80CI'], line=dict(width=0), showlegend=False))
        fig7.add_trace(go.Scatter(x=fc_b.index, y=fc_b['Lower_80CI'], line=dict(width=0), fill='tonexty',
                                   fillcolor='rgba(0,0,0,0.1)', name='80% confidence interval'))
        fig7.update_layout(height=350, yaxis_title="Units/month", hovermode='x unified')
        st.plotly_chart(fig7, use_container_width=True)
