"""Orchestrates the full research pipeline: raw data -> processed research outputs.

This is the single place that wires together data loading, the event study,
sentiment scoring, diffusion modelling, and hypothesis testing. Both
scripts/build_dataset.py (offline, writes JSON to data/processed/) and the
FastAPI backend (can run this live) call into this module so there is one
source of truth for "how the numbers are computed".
"""

from __future__ import annotations

import logging

import pandas as pd

from signalflow import config, diffusion, earnings, event_study, hypotheses, sentiment
from signalflow.data import load_earnings_facts, load_news_headlines, load_price_series, merge_price_series

logger = logging.getLogger(__name__)


def run_full_pipeline(event: config.EventConfig = config.DEFAULT_EVENT) -> dict:
    """Run the entire research pipeline and return a dict with every processed artifact."""
    logger.info("Loading raw data...")
    company_prices = load_price_series(config.META_PRICES_CSV)
    benchmark_prices = load_price_series(config.BENCHMARK_PRICES_CSV)
    facts = load_earnings_facts(config.EARNINGS_FACTS_JSON)
    news_df = load_news_headlines(config.NEWS_HEADLINES_CSV)

    logger.info("Merging price series and running event study...")
    merged = merge_price_series(company_prices, benchmark_prices)
    study = event_study.run_event_study(merged, event)

    logger.info("Computing earnings surprise...")
    earnings_summary = earnings.summarize_surprise(facts)

    logger.info("Scoring news sentiment...")
    scored_news = sentiment.score_headlines(news_df)
    info_intensity = sentiment.daily_information_intensity(scored_news)

    logger.info("Fitting information diffusion models...")
    diffusion_comparison = diffusion.compare_diffusion_models(study["daily"], config.ABSORPTION_THRESHOLDS)

    logger.info("Testing hypotheses...")
    event_df = pd.DataFrame(study["daily"])
    hypothesis_results = hypotheses.run_all_hypotheses(
        earnings_summary, study["summary"], event_df, info_intensity, diffusion_comparison
    )

    return {
        "event": {
            "ticker": event.ticker,
            "company_name": event.company_name,
            "fiscal_quarter": event.fiscal_quarter,
            "announcement_date": event.announcement_date,
            "event_day": event.event_day,
            **facts,
        },
        "earnings_surprise": earnings_summary,
        "event_study": study,
        "news": {
            "headlines": scored_news.assign(date=scored_news["date"].dt.strftime("%Y-%m-%d")).to_dict(
                orient="records"
            ),
            "daily_intensity": info_intensity.to_dict(orient="records"),
        },
        "diffusion": diffusion_comparison,
        "hypotheses": hypothesis_results,
    }
