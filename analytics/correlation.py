import pandas as pd

from config import BENCHMARK_TICKER


def compute_correlation_matrix(prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute pairwise Pearson correlation of daily returns.
    Includes the benchmark if present. Returns a square DataFrame.
    """
    wide = prices_df.pivot(index="date", columns="ticker", values="adj_close")
    wide.index = pd.to_datetime(wide.index)
    wide = wide.sort_index()
    daily_ret = wide.pct_change().dropna(how="all")
    return daily_ret.corr()
