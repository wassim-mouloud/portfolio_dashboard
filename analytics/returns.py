import pandas as pd
import numpy as np


def compute_daily_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Input:  long-format df with columns [ticker, date, adj_close]
    Output: wide-format df with dates as index, tickers as columns, daily % returns as values
    """
    wide = prices_df.pivot(index="date", columns="ticker", values="adj_close")
    wide = wide.sort_index()
    return wide.pct_change().dropna(how="all")


def compute_cumulative_returns(daily_returns: pd.DataFrame) -> pd.DataFrame:
    """Returns cumulative return from the first row (starts at 0)."""
    return (1 + daily_returns).cumprod() - 1


def compute_yoy_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Year-over-year return per ticker.
    Returns a DataFrame with columns [ticker, year, yoy_return_pct].
    """
    wide = prices_df.pivot(index="date", columns="ticker", values="adj_close")
    wide.index = pd.to_datetime(wide.index)
    yearly = wide.resample("YE").last()
    yoy = yearly.pct_change() * 100
    yoy = yoy.stack().reset_index()
    yoy.columns = ["year", "ticker", "yoy_return_pct"]
    yoy["year"] = yoy["year"].dt.year.astype(str)
    return yoy.dropna()


def compute_rolling_mean(prices_df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """Rolling mean of adj_close per ticker. Returns wide-format DataFrame."""
    wide = prices_df.pivot(index="date", columns="ticker", values="adj_close")
    wide.index = pd.to_datetime(wide.index)
    return wide.rolling(window=window).mean()


def compute_peer_comparison(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise all tickers to 100 at their earliest date.
    Returns wide-format DataFrame indexed by date.
    """
    wide = prices_df.pivot(index="date", columns="ticker", values="adj_close")
    wide.index = pd.to_datetime(wide.index)
    wide = wide.sort_index()
    return wide.div(wide.iloc[0]) * 100
