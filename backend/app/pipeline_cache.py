"""Runs the research pipeline once per process and caches the result.

The pipeline is deterministic and cheap (well under a second on the checked-in
dataset), so re-running it on every request would be wasteful for no benefit.
`get_research_result` is a FastAPI dependency; `reset_cache` exists purely for
tests that need a fresh run.
"""
from __future__ import annotations

from functools import lru_cache

from signalflow.pipeline import run_full_pipeline


@lru_cache(maxsize=1)
def get_research_result() -> dict:
    return run_full_pipeline()


def reset_cache() -> None:
    get_research_result.cache_clear()
