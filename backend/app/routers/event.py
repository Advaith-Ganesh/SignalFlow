from fastapi import APIRouter, Depends

from app.pipeline_cache import get_research_result

router = APIRouter(prefix="/api/event", tags=["event"])


@router.get("")
def get_event_overview(result: dict = Depends(get_research_result)) -> dict:
    """Event overview: company, quarter, announcement facts, and earnings surprise."""
    return {
        "event": result["event"],
        "earnings_surprise": result["earnings_surprise"],
    }
