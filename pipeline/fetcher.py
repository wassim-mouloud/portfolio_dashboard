import logging
from typing import List

import pandas as pd
import yfinance as yf

from config import BENCHMARK_TICKER

logger = logging.getLogger(__name__)


def fetch_prices(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    """
    Download daily OHLCV data for the given tickers + benchmark from Yahoo Finance.
    Returns a normalised DataFrame with columns:
        ticker, date, open, high, low, close, adj_close, volume
    """
    all_tickers = list(dict.fromkeys(tickers + [BENCHMARK_TICKER]))  # dedup, preserve order

    logger.info("Fetching %s from %s to %s", all_tickers, start, end)

    raw = yf.download(
        tickers=all_tickers,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
        threads=True,
    )

    if raw.empty:
        raise ValueError(f"No data returned for tickers: {all_tickers}")

    frames = []
    for ticker in all_tickers:
        try:
            if len(all_tickers) == 1:
                df = raw.copy()
            else:
                df = raw.xs(ticker, axis=1, level=1).copy()

            df = df.dropna(subset=["Close"])
            df = df.reset_index()
            df.columns = [c.lower().replace(" ", "_") for c in df.columns]

            # Handle 'adj close' vs 'adj_close' column naming
            if "adj_close" not in df.columns and "adj close" in df.columns:
                df = df.rename(columns={"adj close": "adj_close"})

            df["ticker"] = ticker
            df = df.rename(columns={"date": "date"})
            df["date"] = pd.to_datetime(df["date"]).dt.date

            df = df[["ticker", "date", "open", "high", "low", "close", "adj_close", "volume"]]
            frames.append(df)
            logger.info("  %s: %d rows", ticker, len(df))
        except Exception as exc:
            logger.warning("Skipping %s — %s", ticker, exc)

    if not frames:
        raise ValueError("No valid data fetched for any ticker.")

    return pd.concat(frames, ignore_index=True)
