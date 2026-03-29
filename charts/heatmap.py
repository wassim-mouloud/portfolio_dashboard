import pandas as pd
import plotly.graph_objects as go


def build_correlation_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    tickers = list(corr_matrix.columns)
    z = corr_matrix.values.round(2).tolist()

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=tickers,
        y=tickers,
        colorscale="RdYlGn",
        zmin=-1,
        zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in z],
        texttemplate="%{text}",
        hovertemplate="<b>%{y} vs %{x}</b><br>Correlation: %{z:.2f}<extra></extra>",
    ))

    fig.update_layout(
        title="Return Correlation Matrix",
        template="plotly_dark",
        height=450,
    )
    return fig
