# Architecture

This document describes how SignalFlow is actually built, not an aspirational
design. Every component named here exists in the repository at the path
given.

## System overview

```mermaid
flowchart TD
    subgraph Sources["Real-world data sources"]
        YF["Yahoo Finance public chart API<br/>(no key required)"]
        WEB["Public news articles /<br/>earnings call transcripts"]
    end

    subgraph Raw["data/raw/ (REAL)"]
        PRICES["meta_prices.csv<br/>benchmark_prices.csv"]
        FACTS["earnings_facts.json"]
        NEWS["news_headlines.csv"]
    end

    subgraph Core["src/signalflow/ (core research package)"]
        DATA["data.py<br/>load + validate"]
        EARN["earnings.py<br/>surprise calc"]
        EVENT["event_study.py<br/>market model, AR, CAR"]
        SENT["sentiment.py<br/>VADER scoring"]
        DIFF["diffusion.py<br/>exponential / logistic fit"]
        HYP["hypotheses.py<br/>H1-H4 tests"]
        PIPE["pipeline.py<br/>orchestrator"]
    end

    subgraph Consumers["Everything that uses signalflow"]
        API["backend/app<br/>FastAPI routers"]
        SCRIPT["scripts/build_dataset.py"]
        NB["notebooks/exploratory_analysis.ipynb"]
        TESTS["tests/ (55 pytest tests)"]
    end

    subgraph Frontend["frontend/ (React + TypeScript + Vite)"]
        UI["Dashboard: 6 tabs, Plotly charts"]
    end

    PROC["data/processed/*.json<br/>(DERIVED + MODEL OUTPUT)"]

    YF -->|"scripts/fetch_market_data.py"| PRICES
    WEB -->|"manual research + citation"| FACTS
    WEB -->|"manual research + citation"| NEWS

    PRICES --> DATA
    FACTS --> DATA
    NEWS --> DATA

    DATA --> EARN
    DATA --> EVENT
    DATA --> SENT
    EVENT --> DIFF
    EARN --> HYP
    EVENT --> HYP
    SENT --> HYP
    DIFF --> HYP

    EARN --> PIPE
    EVENT --> PIPE
    SENT --> PIPE
    DIFF --> PIPE
    HYP --> PIPE

    PIPE --> API
    PIPE --> SCRIPT
    PIPE --> NB
    PIPE -.->|"exercised by"| TESTS

    SCRIPT --> PROC
    API -->|"GET /api/*"| UI
```

## Why the package sits in the middle

`src/signalflow/` is the single implementation of every calculation in this
project. Four different consumers call into it:

1. **`backend/app`** — a FastAPI app that calls `run_full_pipeline()` once
   (cached with `functools.lru_cache`) and serves slices of the result as
   read-only JSON.
2. **`scripts/build_dataset.py`** — runs the same pipeline offline and writes
   the result to `data/processed/*.json`, so the numbers are inspectable
   without starting a Python process.
3. **`notebooks/exploratory_analysis.ipynb`** — imports the same functions
   for exploratory plots. Nothing in the notebook re-implements logic that
   lives in the package.
4. **`tests/`** — 55 pytest tests, split between unit tests (synthetic data
   with a known, injected effect — e.g. a fabricated market beta or abnormal
   return shock — checked for exact recovery) and one integration test that
   runs the real pipeline against the real checked-in dataset.

This is a deliberate choice: if the market-model math changed, it changes in
exactly one place, and every consumer picks it up automatically.

## Request lifecycle (dashboard → data)

```mermaid
sequenceDiagram
    participant Browser
    participant Vite as Vite dev server
    participant FastAPI as FastAPI (backend/app)
    participant Cache as pipeline_cache.py
    participant Pipeline as signalflow.pipeline

    Browser->>Vite: GET /
    Vite->>Browser: React app (index.html + bundle)
    Browser->>Vite: fetch('/api/market/event-study')
    Vite->>FastAPI: proxied request (vite.config.ts)
    FastAPI->>Cache: get_research_result()
    alt first request in process lifetime
        Cache->>Pipeline: run_full_pipeline()
        Pipeline->>Pipeline: load raw CSV/JSON, validate,<br/>fit market model, score sentiment,<br/>fit diffusion curves, test hypotheses
        Pipeline-->>Cache: full result dict
    else already cached
        Cache-->>Cache: return cached dict (no recomputation)
    end
    Cache-->>FastAPI: result dict
    FastAPI-->>Browser: JSON (event_study slice)
    Browser->>Browser: render Plotly charts
```

The pipeline is deterministic and takes well under a second on this dataset,
so caching it once per process is the simplest correct choice — there is no
database and no write path anywhere in this system.

## Data classification

Every artifact in this repository is one of four kinds, and the code and
directory structure keep them visibly separate (see `data/README.md` for the
full breakdown per file):

| Kind | Where | Example |
|---|---|---|
| **REAL** | `data/raw/` | Yahoo Finance OHLCV, hand-cited earnings facts, curated headlines |
| **DERIVED** | computed in `src/signalflow/{earnings,event_study}.py` | abnormal returns, earnings surprise % |
| **MODEL OUTPUT** | computed in `src/signalflow/diffusion.py` | fitted exponential/logistic curve parameters |
| **SYNTHETIC** | `tests/` only | fabricated data with a known injected effect, used to verify the math — never presented as real |

## Why not a database

The entire dataset (a handful of CSVs and JSON files covering one company,
one quarter) fits comfortably in memory and is static once fetched — there
is no user-generated data anywhere in the system. Adding a database would
introduce migration/connection-management complexity to solve a problem this
project doesn't have.

## Why not authentication

There is no user-specific data, no write endpoints, and nothing to protect —
every endpoint is a `GET` that returns the same read-only research result to
anyone who asks. Adding auth would protect nothing; see `README.md`'s
Security section and `docs/research_report.md` for the reasoning in full.
