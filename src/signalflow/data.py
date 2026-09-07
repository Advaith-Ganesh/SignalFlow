"""Loading and validating the real, raw input data."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_PRICE_COLUMNS = {"date", "open", "high", "low", "close", "adj_close", "volume"}


class DataValidationError(ValueError):
    """Raised when an input dataset fails a basic sanity check."""


def load_price_series(csv_path: Path) -> pd.DataFrame:
    """Load a daily OHLCV CSV into a validated, date-indexed DataFrame.

    Raises DataValidationError if the file is missing required columns,
    contains non-positive prices, or is not sorted/unique by date.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Price file not found: {csv_path}. Run scripts/fetch_market_data.py first."
        )

    df = pd.read_csv(csv_path)
    missing = REQUIRED_PRICE_COLUMNS - set(df.columns)
    if missing:
        raise DataValidationError(f"{csv_path} is missing columns: {missing}")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    if df["date"].duplicated().any():
        raise DataValidationError(f"{csv_path} contains duplicate dates")

    price_cols = ["open", "high", "low", "close", "adj_close"]
    if (df[price_cols] <= 0).any().any():
        raise DataValidationError(f"{csv_path} contains non-positive prices")

    if (df["volume"] < 0).any():
        raise DataValidationError(f"{csv_path} contains negative volume")

    if df.empty:
        raise DataValidationError(f"{csv_path} contains no rows")

    return df


def load_earnings_facts(json_path: Path) -> dict[str, Any]:
    if not json_path.exists():
        raise FileNotFoundError(f"Earnings facts file not found: {json_path}")
    with json_path.open() as f:
        facts = json.load(f)
    required = {"eps_actual", "eps_estimate", "revenue_actual_usd_billion", "revenue_estimate_usd_billion"}
    missing = required - set(facts)
    if missing:
        raise DataValidationError(f"{json_path} is missing fields: {missing}")
    return facts


def load_news_headlines(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"News headlines file not found: {csv_path}")
    df = pd.read_csv(csv_path)
    required = {"date", "phase", "source", "headline", "url"}
    missing = required - set(df.columns)
    if missing:
        raise DataValidationError(f"{csv_path} is missing columns: {missing}")
    df["date"] = pd.to_datetime(df["date"])
    if df.empty:
        raise DataValidationError(f"{csv_path} contains no rows")
    return df


def merge_price_series(company: pd.DataFrame, benchmark: pd.DataFrame) -> pd.DataFrame:
    """Inner-join company and benchmark prices on date and compute simple returns.

    An inner join is used deliberately: only dates where *both* series traded
    are kept, so market-model regressions never pair a company return with a
    missing/misaligned benchmark observation.
    """
    merged = company.merge(
        benchmark, on="date", suffixes=("_company", "_benchmark"), how="inner"
    ).sort_values("date").reset_index(drop=True)

    if len(merged) < len(company) - 3 and len(merged) < len(benchmark) - 3:
        logger.warning(
            "Merging price series dropped more than 3 rows (company=%d, benchmark=%d, merged=%d); "
            "check for a calendar mismatch.",
            len(company),
            len(benchmark),
            len(merged),
        )

    merged["return_company"] = merged["adj_close_company"].pct_change()
    merged["return_benchmark"] = merged["adj_close_benchmark"].pct_change()
    return merged
