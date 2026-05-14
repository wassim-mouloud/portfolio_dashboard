import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import logging
import streamlit as st
import pandas as pd

from config import DEFAULT_TICKERS, DEFAULT_START_DATE, DEFAULT_RISK_FREE_RATE, BENCHMARK_TICKER
from db.schema import init_db
from pipeline.loader import run_pipeline
from db.repository import get_price_history, get_yoy_returns, get_peer_comparison
from analytics.returns import compute_peer_comparison, compute_yoy_returns
from analytics.risk import build_risk_summary, rolling_volatility
from analytics.correlation import compute_correlation_matrix
from charts.price_chart import build_price_chart
from charts.volatility_chart import build_volatility_chart
from charts.heatmap import build_correlation_heatmap
from charts.yoy_chart import build_yoy_chart

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="Stock Portfolio Dashboard",
    page_icon="📈",
    layout="wide",
)

@st.cache_resource
def get_engine():
    engine = init_db()
    return engine

engine = get_engine()

st.sidebar.title("⚙️ Configuration")

ticker_input = st.sidebar.text_input(
    "Tickers (comma-separated)",
    value=", ".join(DEFAULT_TICKERS),
    help="E.g. AAPL, MSFT, GOOGL",
)
tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start date", value=pd.to_datetime(DEFAULT_START_DATE))
end_date   = col2.date_input("End date",   value=pd.Timestamp.today())

risk_free_rate = st.sidebar.slider(
    "Risk-Free Rate (%)",
    min_value=0.0, max_value=10.0,
    value=DEFAULT_RISK_FREE_RATE * 100, step=0.25,
) / 100

rolling_window = st.sidebar.slider(
    "Rolling Window (days)",
    min_value=10, max_value=90,
    value=30, step=5,
)

force_refresh = st.sidebar.checkbox("Force data refresh", value=False)
load_btn = st.sidebar.button("Load / Refresh Data", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption(f"Benchmark: {BENCHMARK_TICKER} (S&P 500)")

if load_btn or "data_loaded" not in st.session_state:
    with st.spinner("Fetching data from Yahoo Finance..."):
        try:
            summary = run_pipeline(
                engine,
                tickers,
                start=str(start_date),
                end=str(end_date),
                force_refresh=force_refresh,
            )
            if summary:
                st.sidebar.success(f"Loaded: {', '.join(f'{t}({n})' for t, n in summary.items())}")
            else:
                st.sidebar.info("Using cached data.")
            st.session_state["data_loaded"] = True
        except Exception as e:
            st.error(f"Data fetch failed: {e}")
            st.stop()

all_tickers = list(dict.fromkeys(tickers + [BENCHMARK_TICKER]))
prices_df = get_price_history(engine, all_tickers, str(start_date), str(end_date))

if prices_df.empty:
    st.warning("No data found. Click 'Load / Refresh Data'.")
    st.stop()

st.title("📈 Stock Portfolio Risk & Performance Dashboard")
st.caption(f"Data range: {prices_df['date'].min()} → {prices_df['date'].max()}  |  Tickers: {', '.join(tickers)}")

risk_df = build_risk_summary(prices_df, risk_free_rate=risk_free_rate)
cols = st.columns(len(risk_df))
for col, (ticker, row) in zip(cols, risk_df.iterrows()):
    col.metric(
        label=ticker,
        value=row["Total Return"],
        delta=f"Sharpe {row['Sharpe Ratio']}",
    )

st.markdown("---")

peer_wide = compute_peer_comparison(prices_df)
st.plotly_chart(build_price_chart(peer_wide), use_container_width=True)

st.subheader("Risk Metrics")
st.dataframe(risk_df, use_container_width=True)

st.markdown("---")

left, right = st.columns(2)

with left:
    st.plotly_chart(
        build_volatility_chart(prices_df, window=rolling_window),
        use_container_width=True,
    )

with right:
    corr = compute_correlation_matrix(prices_df)
    st.plotly_chart(build_correlation_heatmap(corr), use_container_width=True)

st.markdown("---")

st.subheader("Year-over-Year Returns")

try:
    yoy_df = get_yoy_returns(engine, tickers)
    if yoy_df.empty:
        raise ValueError("Empty SQL result")
except Exception:
    yoy_df = compute_yoy_returns(prices_df[prices_df["ticker"].isin(tickers)])

if not yoy_df.empty:
    st.plotly_chart(build_yoy_chart(yoy_df), use_container_width=True)

st.markdown("---")

with st.expander("🗄️ View SQL Queries used in this dashboard"):
    sql_path = os.path.join(os.path.dirname(__file__), "sql", "queries.sql")
    if os.path.exists(sql_path):
        with open(sql_path) as f:
            st.code(f.read(), language="sql")

st.caption("Data sourced from Yahoo Finance via yfinance. Stored in SQLite. Built with Streamlit + Plotly.")
