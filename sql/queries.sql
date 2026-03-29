-- ============================================================
-- Stock Portfolio Dashboard — Analytical SQL Queries
-- ============================================================


-- 1. Price history for a date range
-- ---------------------------------------------------------------
SELECT ticker, date, adj_close
FROM   price_history
WHERE  ticker IN ('AAPL', 'MSFT', '^GSPC')
  AND  date BETWEEN '2023-01-01' AND '2024-12-31'
ORDER  BY ticker, date;


-- 2. Year-over-Year returns using SQL window functions
-- ---------------------------------------------------------------
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
    WHERE ticker IN ('AAPL', 'MSFT')
)
SELECT DISTINCT
    ticker,
    year,
    ROUND((year_end_price - year_start_price) / year_start_price * 100, 2) AS yoy_return_pct
FROM yearly
ORDER BY ticker, year;


-- 3. 30-day rolling average price
-- ---------------------------------------------------------------
SELECT
    ticker,
    date,
    adj_close,
    AVG(adj_close) OVER (
        PARTITION BY ticker
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_30d
FROM price_history
WHERE ticker = 'AAPL'
ORDER BY date;


-- 4. Peer comparison — prices normalised to 100 at start date
-- ---------------------------------------------------------------
WITH base_prices AS (
    SELECT p.ticker, p.adj_close AS base_price
    FROM   price_history p
    WHERE  p.date = (
        SELECT MIN(date) FROM price_history
        WHERE ticker = p.ticker AND date >= '2024-01-01'
    )
)
SELECT
    ph.ticker,
    ph.date,
    ROUND(ph.adj_close / bp.base_price * 100, 4) AS indexed_price
FROM price_history ph
JOIN base_prices bp ON ph.ticker = bp.ticker
WHERE ph.date >= '2024-01-01'
ORDER BY ph.ticker, ph.date;


-- 5. Latest price per ticker
-- ---------------------------------------------------------------
SELECT ticker, date, adj_close
FROM   price_history
WHERE  (ticker, date) IN (
    SELECT ticker, MAX(date)
    FROM   price_history
    GROUP  BY ticker
);


-- 6. Annualised return per ticker over full date range
-- ---------------------------------------------------------------
WITH endpoints AS (
    SELECT
        ticker,
        FIRST_VALUE(adj_close) OVER (PARTITION BY ticker ORDER BY date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_price,
        LAST_VALUE(adj_close)  OVER (PARTITION BY ticker ORDER BY date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_price,
        COUNT(*) OVER (PARTITION BY ticker) AS trading_days
    FROM price_history
)
SELECT DISTINCT
    ticker,
    ROUND((POWER(last_price / first_price, 252.0 / trading_days) - 1) * 100, 2) AS annualised_return_pct
FROM endpoints
ORDER BY annualised_return_pct DESC;
