from fastapi import APIRouter, Depends

from app.pipeline_cache import get_research_result

router = APIRouter(prefix="/api/diffusion", tags=["diffusion"])


@router.get("")
def get_diffusion(result: dict = Depends(get_research_result)) -> dict:
    """Observed absorption-fraction path, fitted exponential/logistic models, and comparison."""
    return result["diffusion"]
