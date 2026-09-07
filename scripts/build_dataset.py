"""Run the full research pipeline and write processed outputs to data/processed/.

This is the offline counterpart to the backend's live pipeline: running it
produces the exact JSON files the frontend can be pointed at without a
running Python process, and lets `data/processed/` be inspected or diffed
directly.

Usage:
    python scripts/build_dataset.py
"""

from __future__ import annotations

import json
import logging

from signalflow import config
from signalflow.pipeline import run_full_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    result = run_full_pipeline()
    config.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    outputs = {
        "event_overview.json": {"event": result["event"], "earnings_surprise": result["earnings_surprise"]},
        "event_study.json": result["event_study"],
        "news.json": result["news"],
        "diffusion.json": result["diffusion"],
        "hypotheses.json": result["hypotheses"],
    }
    for filename, payload in outputs.items():
        destination = config.PROCESSED_DATA_DIR / filename
        with destination.open("w") as f:
            json.dump(payload, f, indent=2, default=str)
        logger.info("Wrote %s", destination)


if __name__ == "__main__":
    main()
