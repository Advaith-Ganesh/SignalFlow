import pandas as pd

from signalflow.sentiment import (
    classify_compound,
    daily_information_intensity,
    score_headline,
    score_headlines,
)


def test_score_headline_negative():
    scores = score_headline("Facebook stock plummets 26% in its biggest one-day drop ever")
    assert scores["compound"] < -0.05


def test_score_headline_positive():
    scores = score_headline("Meta shares surge after strong earnings beat")
    assert scores["compound"] > 0.05


def test_classify_compound_thresholds():
    assert classify_compound(0.10) == "positive"
    assert classify_compound(-0.10) == "negative"
    assert classify_compound(0.0) == "neutral"


def test_score_headlines_adds_expected_columns():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2022-02-03", "2022-02-03"]),
            "headline": ["Meta shares plunge after weak guidance", "Meta beats revenue estimates"],
        }
    )
    scored = score_headlines(df)
    assert {"sentiment_compound", "sentiment_positive", "sentiment_negative", "sentiment_label"} <= set(
        scored.columns
    )
    assert len(scored) == 2


def test_daily_information_intensity_aggregates_by_day():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2022-02-03", "2022-02-03", "2022-02-04"]),
            "headline": ["a bad headline", "another bad headline", "a good headline"],
        }
    )
    scored = score_headlines(df)
    intensity = daily_information_intensity(scored)
    assert set(intensity["date_str"]) == {"2022-02-03", "2022-02-04"}
    row = intensity[intensity["date_str"] == "2022-02-03"].iloc[0]
    assert row["article_count"] == 2
