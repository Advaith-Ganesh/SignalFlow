import numpy as np
import pytest

from signalflow.diffusion import (
    compare_diffusion_models,
    compute_absorption_fraction,
    empirical_absorption_time,
    exponential_absorption,
    fit_exponential_model,
    fit_logistic_model,
    logistic_diffusion,
)


def test_exponential_absorption_bounds():
    assert exponential_absorption(np.array([0.0]), k=1.0)[0] == pytest.approx(0.0)
    assert exponential_absorption(np.array([100.0]), k=1.0)[0] == pytest.approx(1.0, abs=1e-6)


def test_logistic_diffusion_midpoint():
    # At t == t0, the logistic curve should sit exactly at 0.5
    value = logistic_diffusion(np.array([2.0]), k=1.0, t0=2.0)[0]
    assert value == pytest.approx(0.5)


def test_fit_exponential_model_recovers_known_k():
    t = np.arange(0, 15)
    true_k = 0.6
    fraction = exponential_absorption(t.astype(float), true_k)
    fit = fit_exponential_model(t.astype(float), fraction)
    assert fit["converged"]
    assert fit["k"] == pytest.approx(true_k, rel=0.05)
    assert fit["r_squared"] > 0.99


def test_fit_logistic_model_recovers_known_params():
    t = np.arange(0, 15)
    true_k, true_t0 = 0.8, 5.0
    fraction = logistic_diffusion(t.astype(float), true_k, true_t0)
    fit = fit_logistic_model(t.astype(float), fraction)
    assert fit["converged"]
    assert fit["k"] == pytest.approx(true_k, rel=0.1)
    assert fit["r_squared"] > 0.99


def test_compute_absorption_fraction_normalizes_to_eventual_car():
    records = [
        {"relative_day": -1, "cumulative_abnormal_return": 0.0},
        {"relative_day": 0, "cumulative_abnormal_return": -0.20},
        {"relative_day": 1, "cumulative_abnormal_return": -0.24},
        {"relative_day": 2, "cumulative_abnormal_return": -0.28},
        {"relative_day": 3, "cumulative_abnormal_return": -0.30},
    ]
    result = compute_absorption_fraction(records)
    assert result["eventual_car"] == pytest.approx(-0.30)
    # fraction at the last day must be exactly 1.0 by construction
    assert result["absorption_fraction"][-1] == pytest.approx(1.0)
    # fraction should be increasing since CAR moves monotonically toward eventual_car
    assert all(
        f2 >= f1 - 1e-9 for f1, f2 in zip(result["absorption_fraction"], result["absorption_fraction"][1:])
    )


def test_compute_absorption_fraction_requires_minimum_points():
    with pytest.raises(ValueError):
        compute_absorption_fraction(
            [
                {"relative_day": 0, "cumulative_abnormal_return": -0.1},
                {"relative_day": 1, "cumulative_abnormal_return": -0.2},
            ]
        )


def test_compute_absorption_fraction_rejects_zero_eventual_car():
    with pytest.raises(ValueError):
        compute_absorption_fraction(
            [{"relative_day": i, "cumulative_abnormal_return": 0.0} for i in range(5)]
        )


def test_empirical_absorption_time_interpolates():
    t = np.array([0.0, 1.0, 2.0])
    fraction = np.array([0.0, 0.5, 1.0])
    assert empirical_absorption_time(t, fraction, 0.25) == pytest.approx(0.5)
    assert empirical_absorption_time(t, fraction, 0.75) == pytest.approx(1.5)


def test_empirical_absorption_time_returns_none_if_never_reached():
    t = np.array([0.0, 1.0, 2.0])
    fraction = np.array([0.0, 0.1, 0.2])
    assert empirical_absorption_time(t, fraction, 0.9) is None


def test_compare_diffusion_models_end_to_end():
    records = [
        {"relative_day": d, "cumulative_abnormal_return": -0.30 * exponential_absorption(np.array([float(d)]), 0.5)[0]}
        for d in range(0, 12)
    ]
    result = compare_diffusion_models(records, thresholds=(0.5, 0.9))
    assert result["models"]["exponential"]["converged"]
    assert result["better_fit_model"] in {"exponential", "logistic"}
    assert "p50" in result["information_absorption_time_trading_days"]
    assert "p90" in result["information_absorption_time_trading_days"]
