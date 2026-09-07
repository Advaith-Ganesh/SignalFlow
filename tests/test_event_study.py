import math

import pandas as pd
import pytest

from signalflow.config import EventConfig
from signalflow.event_study import build_event_table, fit_market_model, run_event_study


def _synthetic_merged_prices(n_pre=40, n_post=10, beta=1.2, alpha=0.0, event_shock=-0.20):
    """Construct a fully deterministic price series with a known market-model
    relationship and a known abnormal-return shock on the event day, so the
    event-study math can be checked against hand-computed expectations.
    """
    n = n_pre + 1 + n_post
    dates = pd.bdate_range("2021-01-04", periods=n)

    benchmark_returns = [0.0] + [0.001 if i % 2 == 0 else -0.0008 for i in range(1, n)]
    company_returns = [0.0]
    for i in range(1, n):
        noise = 0.0001 * math.sin(i)
        r = alpha + beta * benchmark_returns[i] + noise
        if i == n_pre:  # event day index
            r += event_shock
        company_returns.append(r)

    # Reconstruct price levels from returns (starting at 100) since run_event_study
    # only consumes the return_* columns and volume_company, not price levels.
    company_price = 100.0
    benchmark_price = 4000.0
    company_prices, benchmark_prices = [], []
    for cr, br in zip(company_returns, benchmark_returns):
        company_price *= 1 + cr
        benchmark_price *= 1 + br
        company_prices.append(company_price)
        benchmark_prices.append(benchmark_price)

    df = pd.DataFrame(
        {
            "date": dates,
            "adj_close_company": company_prices,
            "adj_close_benchmark": benchmark_prices,
            "return_company": company_returns,
            "return_benchmark": benchmark_returns,
            "volume_company": [1_000_000] * n,
            "volume_benchmark": [1_000_000] * n,
        }
    )
    event_config = EventConfig(
        ticker="TEST",
        company_name="Test Co",
        fiscal_quarter="Q_TEST",
        announcement_date=dates[n_pre - 1].strftime("%Y-%m-%d"),
        event_day=dates[n_pre].strftime("%Y-%m-%d"),
        estimation_window_length=n_pre - 5,
        estimation_gap=5,
        event_window_pre=-3,
        event_window_post=n_post,
    )
    return df, event_config


def test_build_event_table_assigns_relative_days():
    df, event = _synthetic_merged_prices()
    table = build_event_table(df, event)
    event_row = table[table["date"] == pd.Timestamp(event.event_day)]
    assert event_row["relative_day"].iloc[0] == 0


def test_build_event_table_missing_event_day_raises():
    df, event = _synthetic_merged_prices()
    bad_event = EventConfig(event_day="1999-01-01")
    with pytest.raises(ValueError):
        build_event_table(df, bad_event)


def test_fit_market_model_recovers_known_beta():
    df, event = _synthetic_merged_prices(beta=1.2, alpha=0.0)
    table = build_event_table(df, event)
    estimation_end = -event.estimation_gap
    estimation_start = estimation_end - event.estimation_window_length
    estimation_df = table[(table["relative_day"] >= estimation_start) & (table["relative_day"] < estimation_end)]

    model = fit_market_model(estimation_df)
    assert model.beta == pytest.approx(1.2, abs=0.05)
    assert model.alpha == pytest.approx(0.0, abs=0.01)


def test_fit_market_model_requires_minimum_observations():
    df, event = _synthetic_merged_prices(n_pre=10, n_post=2)
    table = build_event_table(df, event)
    with pytest.raises(ValueError):
        fit_market_model(table.head(5))


def test_run_event_study_recovers_known_shock():
    df, event = _synthetic_merged_prices(beta=1.2, event_shock=-0.20)
    result = run_event_study(df, event)

    # The abnormal return on the event day should be very close to the
    # injected shock, since the market model was fit on shock-free data.
    assert result["summary"]["event_day_abnormal_return"] == pytest.approx(-0.20, abs=0.01)
    # Highly abnormal, so the t-stat should be large in magnitude.
    assert abs(result["summary"]["event_day_t_stat"]) > 5

    # Cumulative abnormal return should be monotonically defined and include the shock.
    daily = result["daily"]
    event_day_records = [d for d in daily if d["relative_day"] == 0]
    assert len(event_day_records) == 1


def test_run_event_study_cumulative_abnormal_return_is_running_sum():
    df, event = _synthetic_merged_prices()
    result = run_event_study(df, event)
    daily = sorted(result["daily"], key=lambda d: d["relative_day"])
    running_total = 0.0
    for record in daily:
        running_total += record["abnormal_return"]
        assert record["cumulative_abnormal_return"] == pytest.approx(running_total, abs=1e-9)
