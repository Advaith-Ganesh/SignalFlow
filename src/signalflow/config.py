"""Central configuration for the earnings event study.

All "magic numbers" that shape the research design live here, each with a
short justification, so the reasoning behind the design is auditable in one
place rather than scattered through the codebase.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

META_PRICES_CSV = RAW_DATA_DIR / "meta_prices.csv"
BENCHMARK_PRICES_CSV = RAW_DATA_DIR / "benchmark_prices.csv"
EARNINGS_FACTS_JSON = RAW_DATA_DIR / "earnings_facts.json"
NEWS_HEADLINES_CSV = RAW_DATA_DIR / "news_headlines.csv"


@dataclass(frozen=True)
class EventConfig:
    """Defines the event and the study windows around it.

    company: Meta Platforms, Inc. (ticker META)
    event: Q4 FY2021 earnings, released after market close on 2022-02-02.

    Window design:
      - The announcement happened *after* the close on 2022-02-02, so the
        first trading session in which the market could react is
        2022-02-03. That session is defined as event day t=0.
      - estimation_window_length (120 trading days) and estimation_gap
        (10 trading days, ending before the event window) follow the
        standard event-study convention (MacKinlay, 1997): the market-model
        parameters (alpha, beta) are estimated on a "clean" period that
        excludes the event so the event itself cannot bias the benchmark
        relationship.
      - event_window (-5, +10) trading days: five days before the
        announcement lets us check for pre-event drift/information leakage;
        ten days after gives enough runway to see whether the reaction
        stabilizes, while staying short enough that unrelated news is
        unlikely to contaminate the window.
    """

    ticker: str = "META"
    company_name: str = "Meta Platforms, Inc."
    fiscal_quarter: str = "Q4 FY2021"
    announcement_date: str = "2022-02-02"
    event_day: str = "2022-02-03"  # first trading session after the after-hours release
    estimation_window_length: int = 120
    estimation_gap: int = 10
    event_window_pre: int = -5
    event_window_post: int = 10


DEFAULT_EVENT = EventConfig()

# Absorption thresholds reported in the results (fraction of the eventual
# event-window cumulative abnormal return).
ABSORPTION_THRESHOLDS = (0.5, 0.75, 0.9)
