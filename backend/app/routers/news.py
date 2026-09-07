from fastapi import APIRouter, Depends

from app.pipeline_cache import get_research_result

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("")
def get_news(result: dict = Depends(get_research_result)) -> dict:
    """Curated real headlines with VADER sentiment scores, plus daily information intensity."""
    return result["news"]
