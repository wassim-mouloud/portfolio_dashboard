import pandas as pd
import numpy as np

from config import BENCHMARK_TICKER, TRADING_DAYS_PER_YEAR, ROLLING_VOL_WINDOW


def sharpe_ratio(daily_returns: pd.Series, risk_free_rate: float = 0.05) -> float:
    """Annualised Sharpe ratio for a single ticker."""
    excess = daily_returns - risk_free_rate / TRADING_DAYS_PER_YEAR
    if excess.std() == 0:
        return 0.0
    return float((excess.mean() / excess.std()) * np.sqrt(TRADING_DAYS_PER_YEAR))


def beta(ticker_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """Beta of ticker vs benchmark."""
    aligned = pd.concat([ticker_returns, benchmark_returns], axis=1).dropna()
    if aligned.shape[0] < 2:
        return float("nan")
    cov_matrix = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])
    return float(cov_matrix[0, 1] / cov_matrix[1, 1])


def rolling_volatility(daily_returns: pd.Series, window: int = ROLLING_VOL_WINDOW) -> pd.Series:
    """Annualised rolling volatility."""
    return daily_returns.rolling(window=window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)


def max_drawdown(prices: pd.Series) -> float:
    """Maximum peak-to-trough drawdown as a fraction (negative value)."""
    rolling_max = prices.cummax()
    drawdown = (prices - rolling_max) / rolling_max
    return float(drawdown.min())


def build_risk_summary(
    prices_df: pd.DataFrame,
    risk_free_rate: float = 0.05,
) -> pd.DataFrame:
    """
    Compute Sharpe, Beta, Annualised Vol, Max Drawdown for each ticker.
    Excludes the benchmark from the output table but uses it for beta.
    Returns a tidy DataFrame with one row per ticker.
    """
    wide = prices_df.pivot(index="date", columns="ticker", values="adj_close")
    wide.index = pd.to_datetime(wide.index)
    wide = wide.sort_index()

    daily_ret = wide.pct_change().dropna(how="all")

    benchmark_ret = daily_ret[BENCHMARK_TICKER] if BENCHMARK_TICKER in daily_ret.columns else None

    rows = []
    for ticker in daily_ret.columns:
        if ticker == BENCHMARK_TICKER:
            continue
        ret = daily_ret[ticker].dropna()
        price = wide[ticker].dropna()

        sharpe = sharpe_ratio(ret, risk_free_rate)
        b = beta(ret, benchmark_ret) if benchmark_ret is not None else float("nan")
        ann_vol = float(ret.std() * np.sqrt(TRADING_DAYS_PER_YEAR))
        mdd = max_drawdown(price)
        total_return = float((price.iloc[-1] / price.iloc[0]) - 1) if len(price) > 1 else float("nan")

        rows.append({
            "Ticker":           ticker,
            "Total Return":     f"{total_return * 100:.1f}%",
            "Ann. Volatility":  f"{ann_vol * 100:.1f}%",
            "Sharpe Ratio":     round(sharpe, 2),
            "Beta":             round(b, 2),
            "Max Drawdown":     f"{mdd * 100:.1f}%",
        })

    return pd.DataFrame(rows).set_index("Ticker")
