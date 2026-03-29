import pandas as pd
import plotly.express as px


def build_yoy_chart(yoy_df: pd.DataFrame) -> "plotly.graph_objects.Figure":
    """
    yoy_df: columns [ticker, year, yoy_return_pct]
    """
    fig = px.bar(
        yoy_df,
        x="year",
        y="yoy_return_pct",
        color="ticker",
        barmode="group",
        title="Year-over-Year Returns (%)",
        labels={"yoy_return_pct": "YoY Return (%)", "year": "Year"},
        template="plotly_dark",
        height=400,
    )
    fig.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Return: %{y:.1f}%<extra></extra>")
    return fig
