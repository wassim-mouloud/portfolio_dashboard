from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, Text, Float, Date, DateTime, UniqueConstraint, Index,
    text
)
from config import DB_URL

metadata = MetaData()

price_history = Table(
    "price_history",
    metadata,
    Column("id",        Integer, primary_key=True, autoincrement=True),
    Column("ticker",    Text,    nullable=False),
    Column("date",      Date,    nullable=False),
    Column("open",      Float),
    Column("high",      Float),
    Column("low",       Float),
    Column("close",     Float,   nullable=False),
    Column("adj_close", Float,   nullable=False),
    Column("volume",    Integer),
    UniqueConstraint("ticker", "date", name="uq_ticker_date"),
)

fetch_log = Table(
    "fetch_log",
    metadata,
    Column("id",            Integer,  primary_key=True, autoincrement=True),
    Column("ticker",        Text,     nullable=False),
    Column("fetched_at",    DateTime, server_default=text("CURRENT_TIMESTAMP")),
    Column("start_date",    Date,     nullable=False),
    Column("end_date",      Date,     nullable=False),
    Column("rows_inserted", Integer,  nullable=False),
)

Index("idx_price_ticker_date", price_history.c.ticker, price_history.c.date)
Index("idx_price_date",        price_history.c.date)


def get_engine(db_url: str = DB_URL):
    return create_engine(db_url, echo=False)


def init_db(engine=None):
    if engine is None:
        engine = get_engine()
    metadata.create_all(engine)
    return engine
