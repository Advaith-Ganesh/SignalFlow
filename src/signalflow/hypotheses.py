"""Formal statement and testing of the project's four research hypotheses.

Because this project studies a single historical event, hypotheses are
tested with methods that remain valid for n=1 event (event-day significance
tests against the estimation-window null distribution, and within-event
time-series correlation) rather than cross-sectional tests across many
events, which this dataset cannot support. Where a test is necessarily
descriptive/qualitative rather than inferential, that is stated explicitly
in the result rather than dressed up with a fabricated p-value.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def evaluate_h1_surprise_vs_reaction(earnings_summary: dict, event_study_summary: dict) -> dict:
    """H1: A large earnings-related surprise is associated with a large, statistically
    significant abnormal return on the event day.

    Method: classic Brown & Warner (1985) single-event t-test -- the event-day
    abnormal return divided by the estimation-window residual standard
    deviation, compared against the standard normal/t critical value. This
    tests whether the reaction is larger than day-to-day noise would produce
    by chance; it does not (and with one event cannot) establish a
    cross-sectional dose-response relationship between surprise size and
    reaction size.
    """
    t_stat = event_study_summary["event_day_t_stat"]
    p_value = event_study_summary["event_day_p_value"]
    significant = p_value < 0.05

    eps_surprise = earnings_summary["eps_surprise_pct"]
    revenue_surprise = earnings_summary["revenue_surprise_pct"]
    ar = event_study_summary["event_day_abnormal_return"]

    return {
        "hypothesis": "H1",
        "statement": (
            "A large earnings-related surprise is associated with a large, statistically "
            "significant abnormal return on the event day."
        ),
        "variables": {
            "eps_surprise_pct": eps_surprise,
            "revenue_surprise_pct": revenue_surprise,
            "event_day_abnormal_return": ar,
        },
        "method": "Brown & Warner (1985) single-event t-test: AR_0 / sigma(AR_estimation window)",
        "statistic": {"t_stat": t_stat, "p_value": p_value},
        "supported": bool(significant),
        "conclusion": (
            f"The event-day abnormal return ({ar:.2%}) is statistically significant at the 5% level "
            f"(t={t_stat:.2f}, p={p_value:.4f}). Notably the EPS surprise was small and negative "
            f"({eps_surprise:.2f}%) while revenue was a small beat ({revenue_surprise:.2f}%); the huge "
            "abnormal return is far larger than either surprise alone would suggest, indicating the "
            "market was reacting primarily to forward guidance and the first-ever DAU decline rather "
            "than to the earnings/revenue surprise in isolation. With a single event we cannot test "
            "whether *larger* surprises produce *proportionally larger* reactions -- that requires a "
            "cross-sectional sample of many earnings events, which is out of scope here."
            if significant
            else f"The event-day abnormal return ({ar:.2%}) was not statistically significant at the 5% level."
        ),
    }


def evaluate_h2_news_intensity_vs_volume(event_df: pd.DataFrame, info_intensity_df: pd.DataFrame) -> dict:
    """H2: Increased news intensity is associated with increased (abnormal) trading volume.

    Method: Pearson correlation between daily article count and the abnormal
    volume ratio, computed only over trading days inside the event window
    (days without any headline in our small curated dataset are treated as
    zero information intensity, not missing).
    """
    merged = event_df.merge(info_intensity_df, left_on="date", right_on="date_str", how="left")
    merged["article_count"] = merged["article_count"].fillna(0)

    if merged["article_count"].nunique() < 2 or merged["abnormal_volume_ratio"].nunique() < 2:
        corr, p_value = float("nan"), float("nan")
    else:
        corr, p_value = stats.pearsonr(merged["article_count"], merged["abnormal_volume_ratio"])

    n = len(merged)
    n_days_with_news = int((merged["article_count"] > 0).sum())

    return {
        "hypothesis": "H2",
        "statement": "Increased news intensity is associated with increased trading volume.",
        "variables": {"article_count_per_day": "int", "abnormal_volume_ratio": "float"},
        "method": "Pearson correlation, daily article count vs. abnormal volume ratio, event window only",
        "statistic": {"pearson_r": float(corr), "p_value": float(p_value), "n_trading_days": n, "n_days_with_news": n_days_with_news},
        "supported": bool(not np.isnan(corr) and corr > 0.3 and p_value < 0.10),
        "conclusion": (
            f"Pearson r = {corr:.2f} (p={p_value:.3f}) across {n} event-window trading days, only "
            f"{n_days_with_news} of which have a curated headline. This sample is far too small "
            "(n<20, and highly concentrated on the announcement day itself) to support a causal or "
            "even a confidently generalizable correlational claim; the correlation reported here is "
            "descriptive of this one event only, not a validated relationship between news flow and "
            "volume in general."
        ),
    }


def evaluate_h3_fast_adjustment(absorption_times: dict) -> dict:
    """H3: The majority of the event-related price adjustment occurs relatively soon after release."""
    p50 = absorption_times.get("p50")
    p90 = absorption_times.get("p90")
    supported = p50 is not None and p50 <= 1.0

    return {
        "hypothesis": "H3",
        "statement": "The majority of the event-related price adjustment occurs relatively soon after the earnings release.",
        "variables": {"information_absorption_time_p50": p50, "information_absorption_time_p90": p90},
        "method": "Empirical information absorption time: interpolated trading day at which cumulative abnormal return reaches 50%/90% of its eventual (end-of-window) value.",
        "statistic": {"p50_trading_days": p50, "p90_trading_days": p90},
        "supported": bool(supported),
        "conclusion": (
            f"50% of the eventual cumulative abnormal return was absorbed within {p50:.2f} trading day(s), "
            f"and 90% within {p90:.2f} trading day(s)."
            if p50 is not None and p90 is not None
            else "The absorption path did not reach the required thresholds within the observed event window."
        ),
    }


def evaluate_h4_diffusion_model_fit(diffusion_comparison: dict, r_squared_threshold: float = 0.8) -> dict:
    """H4: A diffusion model (exponential or logistic) can approximate the observed CAR path."""
    models = diffusion_comparison["models"]
    best_name = diffusion_comparison["better_fit_model"]
    best = models.get(best_name, {}) if best_name else {}
    r_squared = best.get("r_squared")
    supported = r_squared is not None and r_squared >= r_squared_threshold

    return {
        "hypothesis": "H4",
        "statement": "A diffusion model can approximate the observed cumulative market reaction.",
        "variables": {"exponential_r_squared": models["exponential"].get("r_squared"), "logistic_r_squared": models["logistic"].get("r_squared")},
        "method": f"Nonlinear least-squares fit of both candidate curves to the observed absorption-fraction path; R^2 >= {r_squared_threshold} taken as 'approximates well'.",
        "statistic": {"better_fit_model": best_name, "r_squared": r_squared},
        "supported": bool(supported),
        "conclusion": (
            f"The {best_name} model fit the observed path best (R^2={r_squared:.3f}), which "
            + ("meets" if supported else "falls short of")
            + f" the R^2 >= {r_squared_threshold} bar for calling the approximation good. "
            "With only 16 daily observations dominated by a single one-day jump, both curves are "
            "fitting a near-step function; a strong fit here mainly confirms that absorption was very "
            "fast, not that either functional form is mechanistically 'correct'."
            if r_squared is not None
            else "Neither candidate model converged on the observed data."
        ),
    }


def run_all_hypotheses(
    earnings_summary: dict,
    event_study_summary: dict,
    event_df: pd.DataFrame,
    info_intensity_df: pd.DataFrame,
    diffusion_comparison: dict,
) -> list[dict]:
    return [
        evaluate_h1_surprise_vs_reaction(earnings_summary, event_study_summary),
        evaluate_h2_news_intensity_vs_volume(event_df, info_intensity_df),
        evaluate_h3_fast_adjustment(diffusion_comparison["information_absorption_time_trading_days"]),
        evaluate_h4_diffusion_model_fit(diffusion_comparison),
    ]
