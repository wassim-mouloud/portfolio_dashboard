import logging
from typing import Dict, List

import pandas as pd

from db.repository import upsert_prices, log_fetch, ticker_has_data
from pipeline.fetcher import fetch_prices

logger = logging.getLogger(__name__)


def run_pipeline(
    engine,
    tickers: List[str],
    start: str,
    end: str,
    force_refresh: bool = False,
) -> Dict[str, int]:
    """
    Fetch price data for tickers and store in the database.
    Skips tickers that already have data unless force_refresh=True.
    Returns a dict of {ticker: rows_inserted}.
    """
    tickers_to_fetch = []
    if force_refresh:
        tickers_to_fetch = tickers
    else:
        for t in tickers:
            if not ticker_has_data(engine, t, start, end):
                tickers_to_fetch.append(t)

    if not tickers_to_fetch:
        logger.info("All tickers already in DB — skipping fetch.")
        return {}

    df = fetch_prices(tickers_to_fetch, start, end)
    rows_inserted = upsert_prices(engine, df)

    summary = {}
    for ticker in tickers_to_fetch:
        ticker_rows = len(df[df["ticker"] == ticker])
        summary[ticker] = ticker_rows
        log_fetch(engine, ticker, start, end, ticker_rows)
        logger.info("Loaded %d rows for %s", ticker_rows, ticker)

    return summary
