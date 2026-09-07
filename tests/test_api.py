"""API tests using FastAPI's TestClient (httpx under the hood), against the
real dataset -- no mocking, since the whole point of the API is to expose the
real pipeline output over HTTP.

See conftest.py for how backend/app becomes importable as `app`.
"""

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_event_overview():
    response = client.get("/api/event")
    assert response.status_code == 200
    body = response.json()
    assert body["event"]["ticker"] == "META"
    assert body["earnings_surprise"]["direction"] == "miss"


def test_get_event_study():
    response = client.get("/api/market/event-study")
    assert response.status_code == 200
    body = response.json()
    assert "daily" in body
    assert "market_model" in body
    assert len(body["daily"]) > 0


def test_get_news():
    response = client.get("/api/news")
    assert response.status_code == 200
    body = response.json()
    assert len(body["headlines"]) >= 10
    assert all("sentiment_compound" in h for h in body["headlines"])


def test_get_diffusion():
    response = client.get("/api/diffusion")
    assert response.status_code == 200
    body = response.json()
    assert set(body["models"].keys()) == {"exponential", "logistic"}


def test_get_hypotheses():
    response = client.get("/api/results/hypotheses")
    assert response.status_code == 200
    body = response.json()
    assert len(body["hypotheses"]) == 4


def test_get_limitations():
    response = client.get("/api/results/limitations")
    assert response.status_code == 200
    body = response.json()
    assert len(body["limitations"]) >= 3


def test_get_results_summary():
    response = client.get("/api/results/summary")
    assert response.status_code == 200
    body = response.json()
    assert "event_day_abnormal_return" in body
    assert body["event_day_abnormal_return"] < 0


@pytest.mark.parametrize("path", ["/api/event", "/api/market/event-study", "/api/news", "/api/diffusion"])
def test_cors_headers_present_for_dev_frontend_origin(path):
    response = client.get(path, headers={"Origin": "http://localhost:5173"})
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
