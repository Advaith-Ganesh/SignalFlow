"""Event-study engine: market-model abnormal returns and cumulative abnormal returns.

Methodology follows the standard single-firm event-study framework described
in MacKinlay, A.C. (1997), "Event Studies in Economics and Finance",
Journal of Economic Literature 35(1), 13-39:

1. Estimate a market model  R_it = alpha + beta * R_mt + e_it  on a "clean"
   estimation window that excludes the event.
2. Predict expected returns in the event window using that alpha/beta.
3. Abnormal return AR_t = R_t(actual) - R_t(expected).
4. Cumulative abnormal return CAR(t1, t2) = sum of AR from t1 to t2.
5. Statistical significance of a single event's abnormal return is assessed
   with a t-test that scales the abnormal return by the *estimation-window*
   residual standard deviation (Brown & Warner, 1985, "Using Daily Stock
   Returns: The Case of Event Studies", Journal of Financial Economics).
   This is what makes a "sample size of one event" still testable: the null
   distribution of AR is characterized from the non-event period, not from
   repeated events.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from signalflow.config import EventConfig


@dataclass
class MarketModel:
    alpha: float
    beta: float
    resid_std: float
    n_obs: int
    r_squared: float


def fit_market_model(estimation_df: pd.DataFrame) -> MarketModel:
    """OLS-fit R_company = alpha + beta * R_benchmark on the estimation window."""
    x = estimation_df["return_benchmark"].to_numpy()
    y = estimation_df["return_company"].to_numpy()

    if len(x) < 20:
        raise ValueError(f"Estimation window too short for a reliable market-model fit: {len(x)} obs")

    beta, alpha, r_value, _p_value, _std_err = stats.linregress(x, y)[:5]
    predicted = alpha + beta * x
    residuals = y - predicted
    resid_std = float(np.std(residuals, ddof=2))  # ddof=2: two estimated parameters

    return MarketModel(
        alpha=float(alpha),
        beta=float(beta),
        resid_std=resid_std,
        n_obs=len(x),
        r_squared=float(r_value**2),
    )


def build_event_table(merged_prices: pd.DataFrame, event: EventConfig) -> pd.DataFrame:
    """Assign each trading day a relative-day index around the event day (t=0)."""
    df = merged_prices.copy()
    event_day_ts = pd.Timestamp(event.event_day)
    if event_day_ts not in set(df["date"]):
        raise ValueError(f"Event day {event.event_day} not present in price data")

    event_idx = df.index[df["date"] == event_day_ts][0]
    df["relative_day"] = df.index - event_idx
    return df


def run_event_study(merged_prices: pd.DataFrame, event: EventConfig) -> dict:
    """Full event-study pipeline: fit market model, compute AR/CAR over the event window."""
    if not (event.event_window_pre <= 0 <= event.event_window_post):
        raise ValueError(
            "event_window must contain day 0 (event_window_pre <= 0 <= event_window_post), "
            f"got [{event.event_window_pre}, {event.event_window_post}]"
        )

    df = build_event_table(merged_prices, event)

    estimation_end = -event.estimation_gap
    estimation_start = estimation_end - event.estimation_window_length
    estimation_df = df[(df["relative_day"] >= estimation_start) & (df["relative_day"] < estimation_end)]
    estimation_df = estimation_df.dropna(subset=["return_company", "return_benchmark"])

    model = fit_market_model(estimation_df)

    event_df = df[
        (df["relative_day"] >= event.event_window_pre) & (df["relative_day"] <= event.event_window_post)
    ].copy()
    event_df = event_df.dropna(subset=["return_company", "return_benchmark"])

    event_df["expected_return"] = model.alpha + model.beta * event_df["return_benchmark"]
    event_df["abnormal_return"] = event_df["return_company"] - event_df["expected_return"]
    event_df["cumulative_abnormal_return"] = event_df["abnormal_return"].cumsum()

    # Abnormal volume: ratio of that day's volume to the mean volume in the
    # estimation window, expressed as a multiple (1.0 = "normal" volume).
    mean_estimation_volume = estimation_df["volume_company"].mean()
    event_df["abnormal_volume_ratio"] = event_df["volume_company"] / mean_estimation_volume

    t_stats = event_df["abnormal_return"] / model.resid_std
    event_df["ar_t_stat"] = t_stats
    df_freedom = model.n_obs - 2
    event_df["ar_p_value"] = [
        2 * (1 - stats.t.cdf(abs(t), df=df_freedom)) if pd.notnull(t) else np.nan for t in t_stats
    ]

    max_abs_ar_row = event_df.loc[event_df["abnormal_return"].abs().idxmax()]
    max_abs_car_row = event_df.loc[event_df["cumulative_abnormal_return"].abs().idxmax()]

    post_event = event_df[event_df["relative_day"] > 0]
    pre_event = event_df[event_df["relative_day"] < 0]

    result = {
        "market_model": {
            "alpha": model.alpha,
            "beta": model.beta,
            "resid_std": model.resid_std,
            "n_obs": model.n_obs,
            "r_squared": model.r_squared,
            "estimation_window": [int(estimation_start), int(estimation_end)],
        },
        "event_window": [event.event_window_pre, event.event_window_post],
        "daily": event_df[
            [
                "date",
                "relative_day",
                "return_company",
                "return_benchmark",
                "expected_return",
                "abnormal_return",
                "cumulative_abnormal_return",
                "abnormal_volume_ratio",
                "ar_t_stat",
                "ar_p_value",
                "volume_company",
            ]
        ]
        .assign(date=event_df["date"].dt.strftime("%Y-%m-%d"))
        .to_dict(orient="records"),
        "summary": {
            "car_full_window": float(event_df["cumulative_abnormal_return"].iloc[-1]),
            "mean_pre_event_return": float(pre_event["return_company"].mean()) if len(pre_event) else None,
            "mean_post_event_return": float(post_event["return_company"].mean()) if len(post_event) else None,
            "volatility_pre_event": float(pre_event["return_company"].std()) if len(pre_event) else None,
            "volatility_post_event": float(post_event["return_company"].std()) if len(post_event) else None,
            "volatility_estimation_window": float(estimation_df["return_company"].std()),
            "max_abs_abnormal_return": {
                "relative_day": int(max_abs_ar_row["relative_day"]),
                "date": max_abs_ar_row["date"].strftime("%Y-%m-%d"),
                "value": float(max_abs_ar_row["abnormal_return"]),
            },
            "max_abs_cumulative_abnormal_return": {
                "relative_day": int(max_abs_car_row["relative_day"]),
                "date": max_abs_car_row["date"].strftime("%Y-%m-%d"),
                "value": float(max_abs_car_row["cumulative_abnormal_return"]),
            },
            "event_day_abnormal_return": float(
                event_df.loc[event_df["relative_day"] == 0, "abnormal_return"].iloc[0]
            ),
            "event_day_t_stat": float(event_df.loc[event_df["relative_day"] == 0, "ar_t_stat"].iloc[0]),
            "event_day_p_value": float(event_df.loc[event_df["relative_day"] == 0, "ar_p_value"].iloc[0]),
            "event_day_abnormal_volume_ratio": float(
                event_df.loc[event_df["relative_day"] == 0, "abnormal_volume_ratio"].iloc[0]
            ),
        },
    }
    return result
