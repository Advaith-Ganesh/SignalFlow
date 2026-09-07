"""Information diffusion models fit to the observed cumulative market reaction.

We are not claiming to observe individual investors updating their beliefs.
Instead we ask a narrower, answerable question: does the *shape* of the
cumulative abnormal return path after the announcement resemble a simple,
well-known diffusion/absorption process?

Two candidate curves, both normalized to the fraction of the eventual
event-window cumulative abnormal return (CAR) absorbed by trading day t (t=0
is the announcement reaction day):

  Model A - Exponential absorption:
      f(t) = 1 - exp(-k * t),  k > 0
      A constant-hazard-rate absorption process: at every instant, a fixed
      proportion of the *remaining* unabsorbed information gets priced in.
      This is the natural analogue of "news arrives once, and the market
      digests it at a roughly constant rate" -- and of semi-strong-form
      market efficiency, which predicts most of the adjustment happens
      immediately (t close to 0 already captures most of f).

  Model B - Logistic diffusion:
      f(t) = 1 / (1 + exp(-k * (t - t0)))  , then re-based so f(t_start)=0
      An S-shaped process: slow initial uptake, a fast-adjustment phase, then
      saturation. This is the standard "innovation diffusion" shape (Bass,
      1969) applied to information rather than product adoption -- it is the
      right shape if absorption requires a build-up of attention (e.g.
      through news coverage) before the market reacts fully.

Both are fit with nonlinear least squares (scipy.optimize.curve_fit) and
compared with RMSE, MAE and R^2. We report whichever fits better and are
explicit when neither fits well -- with only 16 daily observations spanning a
single-day, near-instantaneous jump, a poor logistic fit is itself an
informative result about market efficiency, not a modelling failure.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import curve_fit


def exponential_absorption(t: np.ndarray, k: float) -> np.ndarray:
    return 1.0 - np.exp(-k * t)


def logistic_diffusion(t: np.ndarray, k: float, t0: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-k * (t - t0)))


def _goodness_of_fit(observed: np.ndarray, predicted: np.ndarray) -> dict:
    residuals = observed - predicted
    rmse = float(np.sqrt(np.mean(residuals**2)))
    mae = float(np.mean(np.abs(residuals)))
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((observed - np.mean(observed)) ** 2))
    r_squared = float(1 - ss_res / ss_tot) if ss_tot > 0 else float("nan")
    return {"rmse": rmse, "mae": mae, "r_squared": r_squared}


def compute_absorption_fraction(daily_event_records: list[dict]) -> dict:
    """From the event-study daily table, build the empirical absorption-fraction path.

    Only trading days from t=0 (event day) onward are used: the diffusion
    question is "how does the market absorb the news after it arrives",
    so pre-event days (which should show ~no drift under market efficiency)
    are excluded from the curve-fitting sample, though they remain part of
    the event study itself.

    The "eventual" cumulative abnormal return is taken as the CAR value on
    the last day of the event window -- the furthest point we observe.
    """
    post = sorted(
        (r for r in daily_event_records if r["relative_day"] >= 0),
        key=lambda r: r["relative_day"],
    )
    if len(post) < 4:
        raise ValueError("Need at least 4 post-event observations to fit diffusion models")

    t = np.array([r["relative_day"] for r in post], dtype=float)
    car = np.array([r["cumulative_abnormal_return"] for r in post], dtype=float)

    eventual_car = car[-1]
    if eventual_car == 0:
        raise ValueError("Eventual cumulative abnormal return is zero; cannot normalize a fraction")

    # Fraction of the eventual move absorbed by day t. Sign-preserving: if the
    # eventual move is negative, dividing by it flips signs so f is
    # increasing from ~0 toward 1, as the diffusion models assume.
    fraction = car / eventual_car

    return {
        "relative_day": t.tolist(),
        "cumulative_abnormal_return": car.tolist(),
        "eventual_car": float(eventual_car),
        "absorption_fraction": fraction.tolist(),
    }


def fit_exponential_model(t: np.ndarray, fraction: np.ndarray) -> dict:
    try:
        params, _ = curve_fit(exponential_absorption, t, fraction, p0=[0.5], bounds=(1e-6, 10))
    except RuntimeError as exc:
        return {"converged": False, "error": str(exc)}
    predicted = exponential_absorption(t, *params)
    fit = _goodness_of_fit(fraction, predicted)
    return {"converged": True, "k": float(params[0]), **fit}


def fit_logistic_model(t: np.ndarray, fraction: np.ndarray) -> dict:
    try:
        params, _ = curve_fit(
            logistic_diffusion,
            t,
            fraction,
            p0=[1.0, 0.0],
            bounds=([1e-6, t.min() - 5], [10, t.max() + 5]),
            maxfev=5000,
        )
    except RuntimeError as exc:
        return {"converged": False, "error": str(exc)}
    predicted = logistic_diffusion(t, *params)
    fit = _goodness_of_fit(fraction, predicted)
    return {"converged": True, "k": float(params[0]), "t0": float(params[1]), **fit}


def empirical_absorption_time(t: np.ndarray, fraction: np.ndarray, threshold: float) -> float | None:
    """Smallest (linearly interpolated) t at which the empirical fraction path reaches `threshold`.

    Returns None if the path never reaches the threshold within the observed window.
    """
    if fraction[0] >= threshold:
        return float(t[0])
    for i in range(1, len(t)):
        if fraction[i] >= threshold:
            t0, t1 = t[i - 1], t[i]
            f0, f1 = fraction[i - 1], fraction[i]
            if f1 == f0:
                return float(t1)
            interpolated = t0 + (threshold - f0) * (t1 - t0) / (f1 - f0)
            return float(interpolated)
    return None


def compare_diffusion_models(daily_event_records: list[dict], thresholds: tuple[float, ...]) -> dict:
    """Full diffusion-modelling pipeline: build fraction path, fit both models, compare, and
    report information-absorption times from the empirical path.
    """
    absorption = compute_absorption_fraction(daily_event_records)
    t = np.array(absorption["relative_day"])
    fraction = np.array(absorption["absorption_fraction"])

    exponential_fit = fit_exponential_model(t, fraction)
    logistic_fit = fit_logistic_model(t, fraction)

    if exponential_fit.get("converged") and logistic_fit.get("converged"):
        better = "exponential" if exponential_fit["rmse"] <= logistic_fit["rmse"] else "logistic"
    elif exponential_fit.get("converged"):
        better = "exponential"
    elif logistic_fit.get("converged"):
        better = "logistic"
    else:
        better = None

    absorption_times = {
        f"p{int(p * 100)}": empirical_absorption_time(t, fraction, p) for p in thresholds
    }

    return {
        "observed": absorption,
        "models": {
            "exponential": exponential_fit,
            "logistic": logistic_fit,
        },
        "better_fit_model": better,
        "information_absorption_time_trading_days": absorption_times,
    }
