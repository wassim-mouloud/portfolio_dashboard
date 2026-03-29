import pandas as pd
import plotly.graph_objects as go

from config import CHART_COLORS, BENCHMARK_TICKER, ROLLING_VOL_WINDOW
from analytics.risk import rolling_volatility


def build_volatility_chart(prices_df: pd.DataFrame, window: int = ROLLING_VOL_WINDOW) -> go.Figure:
    """
    prices_df: long-format df with [ticker, date, adj_close]
    """
    wide = prices_df.pivot(index="date", columns="ticker", values="adj_close")
    wide.index = pd.to_datetime(wide.index)
    daily_ret = wide.pct_change().dropna(how="all")

    fig = go.Figure()
    for i, ticker in enumerate(daily_ret.columns):
        if ticker == BENCHMARK_TICKER:
            continue
        vol = rolling_volatility(daily_ret[ticker], window=window).dropna()
        color = CHART_COLORS[i % len(CHART_COLORS)]
        fig.add_trace(go.Scatter(
            x=vol.index,
            y=vol * 100,
            mode="lines",
            name=ticker,
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{ticker}</b><br>Date: %{{x|%Y-%m-%d}}<br>Vol: %{{y:.1f}}%<extra></extra>",
        ))

    fig.update_layout(
        title=f"{window}-Day Rolling Annualised Volatility",
        xaxis_title="Date",
        yaxis_title="Volatility (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        template="plotly_dark",
        height=400,
    )
    return fig
