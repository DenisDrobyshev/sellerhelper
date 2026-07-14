"""Stage endpoints — run a pipeline stage over live marketplace data."""

import httpx
from fastapi import APIRouter, Query

from core.collectors.wildberries import WildberriesCollector
from core.engine.demand import validate_demand

router = APIRouter(prefix="/stages", tags=["stages"])


@router.get("/demand")
async def demand(query: str = Query(..., min_length=2), limit: int = 100) -> dict:
    """Stage 2 — validate demand for a query on live Wildberries data."""
    try:
        async with WildberriesCollector() as wb:
            products = await wb.search(query, limit=limit)
    except httpx.HTTPStatusError as exc:
        return {
            "stage": "validate_demand",
            "query": query,
            "passed": False,
            "score": 0.0,
            "reasons": [
                f"data source returned HTTP {exc.response.status_code} (Wildberries "
                "throttling) - retry from a residential/RU IP or set WB_PROXY_URL"
            ],
            "evidence": {},
        }
    result = validate_demand(query, products)
    return {
        "stage": result.stage.value,
        "query": query,
        "passed": result.passed,
        "score": result.score,
        "reasons": result.reasons,
        "evidence": result.evidence,
    }
