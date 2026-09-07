from pathlib import Path

import pandas as pd
import pytest

from signalflow.data import (
    DataValidationError,
    load_earnings_facts,
    load_news_headlines,
    load_price_series,
    merge_price_series,
)


def _write_csv(tmp_path: Path, name: str, rows: list[dict]) -> Path:
    path = tmp_path / name
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _valid_price_rows(n=5, start_price=100.0):
    rows = []
    for i in range(n):
        price = start_price + i
        rows.append(
            {
                "date": f"2022-01-{i + 1:02d}",
                "open": price,
                "high": price + 1,
                "low": price - 1,
                "close": price,
                "adj_close": price,
                "volume": 1_000_000 + i,
            }
        )
    return rows


def test_load_price_series_happy_path(tmp_path):
    path = _write_csv(tmp_path, "prices.csv", _valid_price_rows())
    df = load_price_series(path)
    assert len(df) == 5
    assert list(df.columns) >= ["date", "open", "high", "low", "close", "adj_close", "volume"]
    assert df["date"].is_monotonic_increasing


def test_load_price_series_missing_file():
    with pytest.raises(FileNotFoundError):
        load_price_series(Path("/nonexistent/prices.csv"))


def test_load_price_series_missing_columns(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame([{"date": "2022-01-01", "open": 1.0}]).to_csv(path, index=False)
    with pytest.raises(DataValidationError):
        load_price_series(path)


def test_load_price_series_rejects_non_positive_prices(tmp_path):
    rows = _valid_price_rows()
    rows[0]["close"] = -5.0
    path = _write_csv(tmp_path, "negative.csv", rows)
    with pytest.raises(DataValidationError):
        load_price_series(path)


def test_load_price_series_rejects_duplicate_dates(tmp_path):
    rows = _valid_price_rows()
    rows[1]["date"] = rows[0]["date"]
    path = _write_csv(tmp_path, "dupes.csv", rows)
    with pytest.raises(DataValidationError):
        load_price_series(path)


def test_merge_price_series_computes_returns(tmp_path):
    company = pd.DataFrame(_valid_price_rows(start_price=100.0))
    benchmark = pd.DataFrame(_valid_price_rows(start_price=4000.0))
    company["date"] = pd.to_datetime(company["date"])
    benchmark["date"] = pd.to_datetime(benchmark["date"])

    merged = merge_price_series(company, benchmark)
    assert "return_company" in merged.columns
    assert "return_benchmark" in merged.columns
    # first row's return is NaN (nothing to diff against), rest should be defined
    assert merged["return_company"].iloc[1:].notna().all()
    expected_first_return = (101.0 - 100.0) / 100.0
    assert merged["return_company"].iloc[1] == pytest.approx(expected_first_return)


def test_load_earnings_facts_requires_fields(tmp_path):
    path = tmp_path / "facts.json"
    path.write_text('{"eps_actual": 1.0}')
    with pytest.raises(DataValidationError):
        load_earnings_facts(path)


def test_load_news_headlines_happy_path(tmp_path):
    path = tmp_path / "news.csv"
    pd.DataFrame(
        [
            {
                "date": "2022-02-02",
                "phase": "announcement",
                "source": "Test",
                "headline": "Test headline",
                "url": "http://x",
            }
        ]
    ).to_csv(path, index=False)
    df = load_news_headlines(path)
    assert len(df) == 1
    assert df["date"].iloc[0] == pd.Timestamp("2022-02-02")
