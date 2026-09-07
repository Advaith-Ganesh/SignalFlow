import pytest

from signalflow.earnings import summarize_surprise, surprise_pct


def test_surprise_pct_beat():
    assert surprise_pct(actual=4.0, estimate=2.0) == pytest.approx(100.0)


def test_surprise_pct_miss():
    assert surprise_pct(actual=3.67, estimate=3.84) == pytest.approx(-4.427083, rel=1e-4)


def test_surprise_pct_zero_estimate_raises():
    with pytest.raises(ValueError):
        surprise_pct(actual=1.0, estimate=0.0)


def test_summarize_surprise_direction_labels():
    facts = {
        "eps_actual": 3.67,
        "eps_estimate": 3.84,
        "revenue_actual_usd_billion": 33.67,
        "revenue_estimate_usd_billion": 33.40,
    }
    result = summarize_surprise(facts)
    assert result["direction"] == "miss"
    assert result["eps_surprise_pct"] < 0
    assert result["revenue_surprise_pct"] > 0
