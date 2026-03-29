from datetime import date, datetime
from typing import List

import pandas as pd
from sqlalchemy import text

from db.schema import price_history, fetch_log


def upsert_prices(engine, df: pd.DataFrame) -> int:
    """Insert rows into price_history, ignoring duplicates. Returns rows inserted."""
    rows = df.to_dict(orient="records")
    inserted = 0
    with engine.connect() as conn:
        for row in rows:
            result = conn.execute(
                text("""
                    INSERT OR IGNORE INTO price_history
                        (ticker, date, open, high, low, close, adj_close, volume)
                    VALUES
                        (:ticker, :date, :open, :high, :low, :close, :adj_close, :volume)
                """),
                row,
            )
            inserted += result.rowcount
        conn.commit()
    return inserted


def _to_date(val) -> date:
    if isinstance(val, date):
        return val
    return pd.to_datetime(val).date()


def log_fetch(engine, ticker: str, start, end, rows_inserted: int):
    with engine.connect() as conn:
        conn.execute(
            fetch_log.insert().values(
                ticker=ticker,
                start_date=_to_date(start),
                end_date=_to_date(end),
                rows_inserted=rows_inserted,
            )
        )
        conn.commit()


def get_price_history(
    engine,
    tickers: List[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    placeholders = ", ".join(f":t{i}" for i in range(len(tickers)))
    params = {f"t{i}": t for i, t in enumerate(tickers)}
    params["start"] = start
    params["end"] = end
    query = text(f"""
        SELECT ticker, date, adj_close
        FROM   price_history
        WHERE  ticker IN ({placeholders})
          AND  date BETWEEN :start AND :end
        ORDER  BY ticker, date
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params, parse_dates=["date"])
    return df


def get_yoy_returns(engine, tickers: List[str]) -> pd.DataFrame:
    placeholders = ", ".join(f":t{i}" for i in range(len(tickers)))
    params = {f"t{i}": t for i, t in enumerate(tickers)}
    query = text(f"""
        WITH yearly AS (
            SELECT
                ticker,
                strftime('%Y', date) AS year,
                LAST_VALUE(adj_close) OVER (
                    PARTITION BY ticker, strftime('%Y', date)
                    ORDER BY date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) AS year_end_price,
                FIRST_VALUE(adj_close) OVER (
                    PARTITION BY ticker, strftime('%Y', date)
                    ORDER BY date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) AS year_start_price
            FROM price_history
            WHERE ticker IN ({placeholders})
        )
        SELECT DISTINCT
            ticker,
            year,
            ROUND((year_end_price - year_start_price) / year_start_price * 100, 2) AS yoy_return_pct
        FROM yearly
        ORDER BY ticker, year
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)
    return df


def get_rolling_avg(engine, ticker: str, window: int = 30) -> pd.DataFrame:
    query = text("""
        SELECT
            ticker,
            date,
            adj_close,
            AVG(adj_close) OVER (
                PARTITION BY ticker
                ORDER BY date
                ROWS BETWEEN :window PRECEDING AND CURRENT ROW
            ) AS rolling_avg
        FROM price_history
        WHERE ticker = :ticker
        ORDER BY date
    """)
    with engine.connect() as conn:
        df = pd.read_sql(
            query, conn,
            params={"ticker": ticker, "window": window - 1},
            parse_dates=["date"],
        )
    return df


def get_peer_comparison(engine, tickers: List[str], start: str) -> pd.DataFrame:
    """Returns prices normalised to 100 at start_date for peer comparison."""
    placeholders = ", ".join(f":t{i}" for i in range(len(tickers)))
    params = {f"t{i}": t for i, t in enumerate(tickers)}
    params["start"] = start
    query = text(f"""
        WITH base_prices AS (
            SELECT p.ticker, p.adj_close AS base_price
            FROM   price_history p
            WHERE  p.date = (
                SELECT MIN(date) FROM price_history
                WHERE ticker = p.ticker AND date >= :start
            )
              AND  p.ticker IN ({placeholders})
        )
        SELECT
            ph.ticker,
            ph.date,
            ROUND(ph.adj_close / bp.base_price * 100, 4) AS indexed_price
        FROM price_history ph
        JOIN base_prices bp ON ph.ticker = bp.ticker
        WHERE ph.date >= :start
          AND ph.ticker IN ({placeholders})
        ORDER BY ph.ticker, ph.date
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params, parse_dates=["date"])
    return df


def get_latest_prices(engine, tickers: List[str]) -> pd.DataFrame:
    placeholders = ", ".join(f":t{i}" for i in range(len(tickers)))
    params = {f"t{i}": t for i, t in enumerate(tickers)}
    query = text(f"""
        SELECT ticker, date, adj_close
        FROM   price_history
        WHERE  ticker IN ({placeholders})
          AND  (ticker, date) IN (
              SELECT ticker, MAX(date)
              FROM   price_history
              WHERE  ticker IN ({placeholders})
              GROUP  BY ticker
          )
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params, parse_dates=["date"])
    return df


def ticker_has_data(engine, ticker: str, start: str, end: str) -> bool:
    query = text("""
        SELECT COUNT(*) AS cnt
        FROM price_history
        WHERE ticker = :ticker AND date BETWEEN :start AND :end
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"ticker": ticker, "start": start, "end": end})
        return result.scalar() > 0
