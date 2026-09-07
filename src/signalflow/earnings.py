"""Earnings and revenue surprise calculations."""
from __future__ import annotations


def surprise_pct(actual: float, estimate: float) -> float:
    """Percentage surprise = (actual - estimate) / |estimate| * 100.

    Standard SUE-style (standardized unexpected earnings) surprise measure.
    Returns a percentage (e.g. -4.43 means actual missed estimate by 4.43%).
    """
    if estimate == 0:
        raise ValueError("Cannot compute a percentage surprise against an estimate of zero")
    return (actual - estimate) / abs(estimate) * 100.0


def summarize_surprise(facts: dict) -> dict:
    """Compute EPS and revenue surprise from a loaded earnings_facts.json dict."""
    eps_surprise = surprise_pct(facts["eps_actual"], facts["eps_estimate"])
    revenue_surprise = surprise_pct(
        facts["revenue_actual_usd_billion"], facts["revenue_estimate_usd_billion"]
    )
    return {
        "eps_actual": facts["eps_actual"],
        "eps_estimate": facts["eps_estimate"],
        "eps_surprise_pct": round(eps_surprise, 4),
        "revenue_actual_usd_billion": facts["revenue_actual_usd_billion"],
        "revenue_estimate_usd_billion": facts["revenue_estimate_usd_billion"],
        "revenue_surprise_pct": round(revenue_surprise, 4),
        "direction": "miss" if eps_surprise < 0 else ("beat" if eps_surprise > 0 else "in-line"),
    }
