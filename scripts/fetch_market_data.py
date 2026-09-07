"""Fetch real historical daily OHLCV data from Yahoo Finance's public chart API.

This uses the same unauthenticated endpoint that the popular `yfinance` library
wraps (https://query1.finance.yahoo.com/v8/finance/chart/<symbol>). No API key
is required. Data is written as-is to data/raw/ as CSV so the rest of the
pipeline never has to touch the network again.

Usage:
    python scripts/fetch_market_data.py
"""

from __future__ import annotations

import csv
import datetime as dt
import logging
import time
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 (SignalFlow research project)"}

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# Date range chosen to give a ~150-trading-day estimation window before the
# event plus a comfortable post-event tail for diffusion modelling.
START_DATE = "2021-06-01"
END_DATE = "2022-04-15"

SYMBOLS = {
    "META": "meta_prices.csv",
    "%5EGSPC": "benchmark_prices.csv",  # S&P 500 index, used as the market benchmark
}


def _to_unix(date_str: str) -> int:
    return int(dt.datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp())


def fetch_daily_ohlcv(symbol: str, start: str, end: str, retries: int = 3) -> dict:
    """Fetch raw daily OHLCV JSON for a symbol from Yahoo Finance's chart API."""
    params = {
        "period1": _to_unix(start),
        "period2": _to_unix(end),
        "interval": "1d",
        "events": "div,split",
    }
    url = YAHOO_CHART_URL.format(symbol=symbol)
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:  # pragma: no cover - network flakiness
            last_error = exc
            logger.warning("Attempt %d/%d failed for %s: %s", attempt, retries, symbol, exc)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Failed to fetch {symbol} after {retries} attempts") from last_error


def write_csv(payload: dict, destination: Path) -> int:
    """Flatten the Yahoo chart JSON payload into a clean OHLCV CSV file."""
    result = payload["chart"]["result"][0]
    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]
    adjclose = result["indicators"]["adjclose"][0]["adjclose"]

    rows = []
    for i, ts in enumerate(timestamps):
        # Skip rows with missing data (holidays/partial sessions occasionally appear as nulls)
        if quote["close"][i] is None:
            continue
        date = dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).strftime("%Y-%m-%d")
        rows.append(
            {
                "date": date,
                "open": quote["open"][i],
                "high": quote["high"][i],
                "low": quote["low"][i],
                "close": quote["close"][i],
                "adj_close": adjclose[i],
                "volume": quote["volume"][i],
            }
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "open", "high", "low", "close", "adj_close", "volume"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    for symbol, filename in SYMBOLS.items():
        logger.info("Fetching %s (%s to %s)...", symbol, START_DATE, END_DATE)
        payload = fetch_daily_ohlcv(symbol, START_DATE, END_DATE)
        destination = RAW_DATA_DIR / filename
        n_rows = write_csv(payload, destination)
        logger.info("Wrote %d rows to %s", n_rows, destination)


if __name__ == "__main__":
    main()
