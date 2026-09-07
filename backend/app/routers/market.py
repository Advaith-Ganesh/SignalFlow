from fastapi import APIRouter, Depends

from app.pipeline_cache import get_research_result

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/event-study")
def get_event_study(result: dict = Depends(get_research_result)) -> dict:
    """Market model parameters, daily abnormal/cumulative-abnormal returns, and summary stats."""
    return result["event_study"]
