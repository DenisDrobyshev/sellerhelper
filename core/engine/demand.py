"""Stage 2 — Validate demand.

Turns a snapshot of the top marketplace products for a query into a demand
verdict. The gate passes when there is proven buying activity (reviews across
the top sellers) in a market that is not trivially thin.

Trend direction ("not declining") needs historized snapshots and lands with the
cloud data layer (see ROADMAP). v0 evaluates the demand *level* from a single
snapshot and is explicit that the trend is not yet assessed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import log10

from core.engine.stages import GateResult, Stage
from core.models.product import Product

# Tunable gate thresholds — conservative defaults for a first pass.
DEFAULT_MIN_PRODUCTS = 10
DEFAULT_MIN_TOTAL_REVIEWS = 2000


def _percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    s = sorted(values)
    if len(s) == 1:
        return round(s[0], 2)
    k = (len(s) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return round(s[lo] + (s[hi] - s[lo]) * (k - lo), 2)


@dataclass
class DemandMetrics:
    query: str
    products_analyzed: int
    total_reviews: int
    median_reviews: float | None
    reviewed_share: float           # fraction of products carrying any reviews
    price_median: float | None
    price_p25: float | None
    price_p75: float | None
    avg_rating: float | None


def analyze_demand(query: str, products: list[Product]) -> DemandMetrics:
    reviews = [p.reviews or 0 for p in products]
    prices = [p.price for p in products if p.price]
    ratings = [p.rating for p in products if p.rating]
    reviewed = [r for r in reviews if r > 0]
    return DemandMetrics(
        query=query,
        products_analyzed=len(products),
        total_reviews=sum(reviews),
        median_reviews=_percentile([float(r) for r in reviews], 0.5),
        reviewed_share=round(len(reviewed) / len(products), 2) if products else 0.0,
        price_median=_percentile(prices, 0.5),
        price_p25=_percentile(prices, 0.25),
        price_p75=_percentile(prices, 0.75),
        avg_rating=round(sum(ratings) / len(ratings), 2) if ratings else None,
    )


def demand_score(m: DemandMetrics) -> float:
    """0..1 — a log-scaled read of buying activity (~100k+ reviews approaches 1.0)."""
    if m.total_reviews <= 0:
        return 0.0
    return round(min(1.0, log10(m.total_reviews + 1) / 5), 2)


def validate_demand(
    query: str,
    products: list[Product],
    *,
    min_products: int = DEFAULT_MIN_PRODUCTS,
    min_total_reviews: int = DEFAULT_MIN_TOTAL_REVIEWS,
) -> GateResult:
    """Run the Stage 2 gate over a product snapshot and return a GateResult."""
    m = analyze_demand(query, products)
    reasons: list[str] = []
    passed = True

    if m.products_analyzed < min_products:
        passed = False
        reasons.append(
            f"only {m.products_analyzed} products found (need >= {min_products}) "
            "- market too thin, or the data source was blocked"
        )
    if m.total_reviews < min_total_reviews:
        passed = False
        reasons.append(
            f"{m.total_reviews} reviews across the top {m.products_analyzed} products "
            f"- weak buying signal (need >= {min_total_reviews})"
        )
    else:
        reasons.append(
            f"{m.total_reviews} reviews across the top {m.products_analyzed} products "
            "- real, active demand"
        )
    if m.price_median:
        reasons.append(
            f"price corridor ~ {m.price_p25}-{m.price_p75} RUB (median {m.price_median} RUB)"
        )
    reasons.append(
        "trend direction not evaluated in v0 - requires historized snapshots (roadmap)"
    )

    return GateResult(
        stage=Stage.VALIDATE_DEMAND,
        passed=passed,
        score=demand_score(m),
        reasons=reasons,
        evidence=asdict(m),
    )


async def _demo(query: str) -> None:
    import httpx

    from core.collectors.wildberries import WildberriesCollector

    try:
        async with WildberriesCollector() as wb:
            products = await wb.search(query, limit=100)
    except httpx.HTTPStatusError as exc:
        code = exc.response.status_code
        print(f"\nData source error for {query!r}: HTTP {code}.")
        if code == 429:
            print("Wildberries throttled the request - retry from a residential/RU IP, "
                  "set WB_PROXY_URL, or wait for the limit to reset.")
        return
    result = validate_demand(query, products)
    print(f"\nStage 2 . Validate demand - {query!r}")
    print(f"  verdict: {'PASS' if result.passed else 'FAIL'}   demand score: {result.score}")
    for r in result.reasons:
        print(f"   - {r}")


if __name__ == "__main__":
    import asyncio
    import sys

    asyncio.run(_demo(" ".join(sys.argv[1:]) or "чехол для iphone"))
