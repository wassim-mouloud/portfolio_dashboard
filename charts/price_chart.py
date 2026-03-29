import pandas as pd
import plotly.graph_objects as go

from config import CHART_COLORS, BENCHMARK_TICKER


def build_price_chart(peer_df: pd.DataFrame) -> go.Figure:
    """
    peer_df: wide-format DataFrame indexed by date, columns = tickers,
             values = price normalised to 100 at start.
    """
    fig = go.Figure()

    for i, ticker in enumerate(peer_df.columns):
        color = CHART_COLORS[i % len(CHART_COLORS)]
        dash = "dot" if ticker == BENCHMARK_TICKER else "solid"
        fig.add_trace(go.Scatter(
            x=peer_df.index,
            y=peer_df[ticker],
            mode="lines",
            name=ticker,
            line=dict(color=color, width=2, dash=dash),
            hovertemplate=f"<b>{ticker}</b><br>Date: %{{x|%Y-%m-%d}}<br>Index: %{{y:.1f}}<extra></extra>",
        ))

    fig.update_layout(
        title="Relative Price Performance (Base = 100)",
        xaxis_title="Date",
        yaxis_title="Indexed Price",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1,  label="1M",  step="month", stepmode="backward"),
                    dict(count=3,  label="3M",  step="month", stepmode="backward"),
                    dict(count=6,  label="6M",  step="month", stepmode="backward"),
                    dict(count=1,  label="YTD", step="year",  stepmode="todate"),
                    dict(count=1,  label="1Y",  step="year",  stepmode="backward"),
                    dict(step="all", label="All"),
                ]
            ),
            rangeslider=dict(visible=True),
            type="date",
        ),
        template="plotly_dark",
        height=500,
    )
    return fig
