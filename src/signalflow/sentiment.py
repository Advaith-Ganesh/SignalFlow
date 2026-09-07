"""Lightweight financial-news sentiment scoring.

We use VADER (Valence Aware Dictionary and sEntiment Reasoner; Hutto & Gilbert,
2014) rather than a heavier model like FinBERT for a deliberate reason: our
input is a small set of short headlines (metadata, not full articles), VADER
is a rule-based lexicon method that needs no training data or GPU, runs fully
offline once installed, and is a standard, well-understood baseline for
short-text sentiment. A transformer such as FinBERT would add a large
dependency and inference cost for a feature that, on 13 headlines, would not
be statistically distinguishable from a simpler method. VADER's compound
score is also easy to reason about and explain, which matters for a project
whose goal is a transparent, reproducible research pipeline rather than
maximizing NLP benchmark accuracy.
"""
from __future__ import annotations

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

# Headlines in this domain routinely use words VADER's general-purpose lexicon
# scores as strongly negative/positive out of financial context (e.g. "miss",
# "beat", "plunge", "surge", "wipeout"). A small domain lexicon addition keeps
# the method simple (still VADER) while correcting the most obvious
# financial-domain mismatches, a common lightweight adaptation documented in
# VADER's own README for domain-specific extensions.
_FINANCE_LEXICON_UPDATE = {
    "plummets": -3.4,
    "plunge": -3.0,
    "plunges": -3.0,
    "wipeout": -3.2,
    "tumbles": -2.6,
    "tanks": -2.6,
    "slumps": -2.2,
    "slash": -1.8,
    "downgrade": -2.0,
    "downgraded": -2.0,
    "miss": -1.6,
    "misses": -1.6,
    "beat": 2.0,
    "beats": 2.0,
    "surge": 2.6,
    "surges": 2.6,
    "soar": 2.8,
    "soars": 2.8,
    "rebound": 1.8,
    "recovery": 1.6,
}
_analyzer.lexicon.update(_FINANCE_LEXICON_UPDATE)


def score_headline(headline: str) -> dict:
    """Return VADER's neg/neu/pos/compound scores for one headline."""
    return _analyzer.polarity_scores(headline)


def classify_compound(compound: float) -> str:
    """VADER's own recommended thresholds for classifying the compound score."""
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"


def score_headlines(news_df: pd.DataFrame) -> pd.DataFrame:
    """Add sentiment columns to a news headlines DataFrame (see data.load_news_headlines)."""
    df = news_df.copy()
    scores = df["headline"].apply(score_headline)
    df["sentiment_compound"] = scores.apply(lambda s: s["compound"])
    df["sentiment_positive"] = scores.apply(lambda s: s["pos"])
    df["sentiment_negative"] = scores.apply(lambda s: s["neg"])
    df["sentiment_label"] = df["sentiment_compound"].apply(classify_compound)
    return df


def daily_information_intensity(scored_news_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-day article count and mean sentiment ("information intensity")."""
    grouped = (
        scored_news_df.groupby(scored_news_df["date"].dt.strftime("%Y-%m-%d"))
        .agg(
            article_count=("headline", "count"),
            mean_sentiment=("sentiment_compound", "mean"),
        )
        .reset_index()
        .rename(columns={"date": "date_str"})
    )
    return grouped
