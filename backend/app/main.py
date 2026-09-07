"""SignalFlow research API.

Serves the results of the offline-reproducible information-diffusion event
study over HTTP for the React dashboard. All computation lives in the
`signalflow` package (src/signalflow/); this app is a thin read-only view
over `signalflow.pipeline.run_full_pipeline()`.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import diffusion, event, market, news, results

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="SignalFlow Research API",
    description=(
        "Information Diffusion and Market Reaction: a historical earnings event study "
        "on Meta Platforms' Q4 FY2021 earnings release."
    ),
    version="1.0.0",
)

# The dashboard runs on Vite's default dev port during development. In a
# packaged/deployed setting the frontend would typically be served from the
# same origin, but permissive local CORS keeps `npm run dev` frictionless.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(event.router)
app.include_router(market.router)
app.include_router(news.router)
app.include_router(diffusion.router)
app.include_router(results.router)


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/")
def root() -> dict:
    """Basic API index so hitting the bare server URL isn't a bare 404."""
    return {
        "name": "SignalFlow Research API",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": [
            "/api/event",
            "/api/market/event-study",
            "/api/news",
            "/api/diffusion",
            "/api/results/hypotheses",
            "/api/results/limitations",
            "/api/results/summary",
        ],
    }
