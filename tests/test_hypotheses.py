import pandas as pd

from signalflow.hypotheses import (
    evaluate_h1_surprise_vs_reaction,
    evaluate_h2_news_intensity_vs_volume,
    evaluate_h3_fast_adjustment,
    evaluate_h4_diffusion_model_fit,
)


def test_h1_significant_case():
    earnings_summary = {"eps_surprise_pct": -4.43, "revenue_surprise_pct": 0.81}
    event_summary = {
        "event_day_abnormal_return": -0.23,
        "event_day_t_stat": -15.9,
        "event_day_p_value": 0.0001,
    }
    result = evaluate_h1_surprise_vs_reaction(earnings_summary, event_summary)
    assert result["supported"] is True
    assert result["hypothesis"] == "H1"


def test_h1_not_significant_case():
    earnings_summary = {"eps_surprise_pct": 0.1, "revenue_surprise_pct": 0.1}
    event_summary = {"event_day_abnormal_return": 0.001, "event_day_t_stat": 0.2, "event_day_p_value": 0.8}
    result = evaluate_h1_surprise_vs_reaction(earnings_summary, event_summary)
    assert result["supported"] is False


def test_h2_positive_correlation_detected():
    event_df = pd.DataFrame(
        {
            "date": ["2022-02-01", "2022-02-02", "2022-02-03", "2022-02-04", "2022-02-05"],
            "abnormal_volume_ratio": [1.0, 1.2, 8.0, 3.0, 1.1],
        }
    )
    info_df = pd.DataFrame(
        {
            "date_str": ["2022-02-01", "2022-02-02", "2022-02-03", "2022-02-04", "2022-02-05"],
            "article_count": [0, 1, 5, 2, 0],
        }
    )
    result = evaluate_h2_news_intensity_vs_volume(event_df, info_df)
    assert result["hypothesis"] == "H2"
    assert result["statistic"]["pearson_r"] > 0


def test_h2_handles_missing_news_days():
    event_df = pd.DataFrame({"date": ["2022-02-01", "2022-02-02"], "abnormal_volume_ratio": [1.0, 1.1]})
    info_df = pd.DataFrame({"date_str": [], "article_count": []})
    result = evaluate_h2_news_intensity_vs_volume(event_df, info_df)
    assert result["statistic"]["n_days_with_news"] == 0


def test_h3_fast_absorption_supported():
    result = evaluate_h3_fast_adjustment({"p50": 0.0, "p75": 1.2, "p90": 2.3})
    assert result["supported"] is True


def test_h3_slow_absorption_not_supported():
    result = evaluate_h3_fast_adjustment({"p50": 5.0, "p75": 8.0, "p90": None})
    assert result["supported"] is False


def test_h4_good_fit_supported():
    diffusion_comparison = {
        "models": {
            "exponential": {"r_squared": 0.95},
            "logistic": {"r_squared": 0.5},
        },
        "better_fit_model": "exponential",
    }
    result = evaluate_h4_diffusion_model_fit(diffusion_comparison, r_squared_threshold=0.8)
    assert result["supported"] is True


def test_h4_poor_fit_not_supported():
    diffusion_comparison = {
        "models": {
            "exponential": {"r_squared": -5.0},
            "logistic": {"r_squared": 0.58},
        },
        "better_fit_model": "logistic",
    }
    result = evaluate_h4_diffusion_model_fit(diffusion_comparison, r_squared_threshold=0.8)
    assert result["supported"] is False
