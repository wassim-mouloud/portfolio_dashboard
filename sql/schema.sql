-- ============================================================
-- Stock Portfolio Dashboard — SQLite Schema
-- ============================================================

CREATE TABLE IF NOT EXISTS price_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker      TEXT    NOT NULL,
    date        DATE    NOT NULL,
    open        REAL,
    high        REAL,
    low         REAL,
    close       REAL    NOT NULL,
    adj_close   REAL    NOT NULL,   -- used for all return calculations
    volume      INTEGER,
    UNIQUE (ticker, date)           -- enables INSERT OR IGNORE idempotency
);

CREATE TABLE IF NOT EXISTS fetch_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker        TEXT     NOT NULL,
    fetched_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    start_date    DATE     NOT NULL,
    end_date      DATE     NOT NULL,
    rows_inserted INTEGER  NOT NULL
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_price_ticker_date ON price_history (ticker, date);
CREATE INDEX IF NOT EXISTS idx_price_date        ON price_history (date);
