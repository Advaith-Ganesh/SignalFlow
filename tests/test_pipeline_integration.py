"""End-to-end integration test against the real, checked-in historical dataset.

This intentionally hits the real CSV/JSON files in data/raw/ rather than
synthetic fixtures, so a change that breaks the actual research pipeline (not
just a unit in isolation) is caught. It only checks broad, robust properties
of the real Meta Platforms Q4 2021 event -- not exact floating point values,
since those would make the test brittle to any methodological refinement.
"""
from signalflow.pipeline import run_full_pipeline


def test_full_pipeline_runs_and_matches_known_facts():
    result = run_full_pipeline()

    assert result["event"]["ticker"] == "META"
    assert result["earnings_surprise"]["direction"] == "miss"

    summary = result["event_study"]["summary"]
    # The real-world reaction was an extreme, well-documented ~-23% to -26% one-day move.
    assert summary["event_day_abnormal_return"] < -0.15
    assert summary["event_day_p_value"] < 0.05

    diffusion_result = result["diffusion"]
    assert diffusion_result["models"]["exponential"]["converged"]
    assert diffusion_result["models"]["logistic"]["converged"]

    assert len(result["hypotheses"]) == 4
    hypothesis_ids = {h["hypothesis"] for h in result["hypotheses"]}
    assert hypothesis_ids == {"H1", "H2", "H3", "H4"}

    # H1 (a significant reaction occurred) should hold for this event regardless
    # of any minor tuning of the estimation window.
    h1 = next(h for h in result["hypotheses"] if h["hypothesis"] == "H1")
    assert h1["supported"] is True
