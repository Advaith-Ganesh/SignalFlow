from fastapi import APIRouter, Depends

from app.pipeline_cache import get_research_result

router = APIRouter(prefix="/api/results", tags=["results"])

LIMITATIONS = [
    {
        "title": "Single-event study",
        "detail": (
            "This project studies exactly one earnings event. Every statistic here describes what "
            "happened to META around February 2-3, 2022 -- it is not a validated general model of "
            "'how markets react to earnings', which would require many events across many firms and "
            "market regimes."
        ),
    },
    {
        "title": "Daily, not intraday, granularity",
        "detail": (
            "Free, no-API-key historical intraday data is not available for a date this far in the "
            "past, so the event study and diffusion models operate on daily closes. Because roughly "
            "70% of the eventual cumulative abnormal return was already realized by the close of the "
            "announcement-reaction day itself, this project cannot resolve *within-day* absorption "
            "dynamics (e.g. the first five minutes of after-hours trading vs. the next morning's open)."
        ),
    },
    {
        "title": "Market model, not a full risk model",
        "detail": (
            "Abnormal returns are computed against a single-factor market model (S&P 500 as the "
            "market proxy). No size, value, momentum, or sector factors are controlled for, so some "
            "of the 'abnormal' return could in principle reflect factor exposures rather than pure "
            "firm-specific news."
        ),
    },
    {
        "title": "Small, curated news sample",
        "detail": (
            "The news dataset is 13 manually curated real headlines, not a comprehensive news feed. "
            "The news-intensity vs. volume correlation (H2) is reported for transparency but should "
            "be read as descriptive of this one event's timeline, not a statistically powered test of "
            "a general news-volume relationship."
        ),
    },
    {
        "title": "Diffusion curves are descriptive fits, not causal mechanisms",
        "detail": (
            "The exponential and logistic curves are standard, simple functional forms fit to the "
            "observed cumulative abnormal return path. A good fit shows the *shape* of the observed "
            "reaction is consistent with a given absorption pattern; it does not prove investors "
            "literally follow that mathematical process."
        ),
    },
    {
        "title": "No forward-looking claims",
        "detail": (
            "Nothing in this project predicts future stock prices or is intended for trading use. "
            "The research question is about how a specific, already-realized event was absorbed into "
            "price -- an explanatory, historical analysis, not a forecasting model."
        ),
    },
]


@router.get("/hypotheses")
def get_hypotheses(result: dict = Depends(get_research_result)) -> dict:
    return {"hypotheses": result["hypotheses"]}


@router.get("/limitations")
def get_limitations() -> dict:
    return {"limitations": LIMITATIONS}


@router.get("/summary")
def get_results_summary(result: dict = Depends(get_research_result)) -> dict:
    """A single endpoint bundling the headline numbers the dashboard's 'Results' section needs."""
    event_summary = result["event_study"]["summary"]
    diffusion_result = result["diffusion"]
    return {
        "earnings_surprise": result["earnings_surprise"],
        "event_day_abnormal_return": event_summary["event_day_abnormal_return"],
        "event_day_p_value": event_summary["event_day_p_value"],
        "car_full_window": event_summary["car_full_window"],
        "better_fit_model": diffusion_result["better_fit_model"],
        "model_metrics": diffusion_result["models"],
        "information_absorption_time_trading_days": diffusion_result["information_absorption_time_trading_days"],
        "hypotheses": result["hypotheses"],
    }
