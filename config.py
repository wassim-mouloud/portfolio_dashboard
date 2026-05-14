import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "portfolio.db")
DB_URL = f"sqlite:///{DB_PATH}"

DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN"]
BENCHMARK_TICKER = "^GSPC"
DEFAULT_START_DATE = "2022-01-01"
DEFAULT_RISK_FREE_RATE = 0.05  # 5% annualised

ROLLING_VOL_WINDOW = 30   # days
ROLLING_AVG_WINDOW = 30   # days
TRADING_DAYS_PER_YEAR = 252

CHART_COLORS = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA",
    "#FFA15A", "#19D3F3", "#FF6692", "#B6E880"
]
  