"""Unit tests for Stage 2 (demand validation) — pure logic, no network."""

from core.engine.demand import analyze_demand, demand_score, validate_demand
from core.engine.stages import Stage
from core.models.product import Product


def _p(reviews: int, price: float, rating: float = 4.6) -> Product:
    return Product(
        marketplace="wildberries", external_id=1, name="item",
        reviews=reviews, price=price, rating=rating,
    )


def test_analyze_aggregates():
    products = [_p(100, 500), _p(0, 700), _p(50, 900)]
    m = analyze_demand("q", products)
    assert m.products_analyzed == 3
    assert m.total_reviews == 150
    assert m.reviewed_share == round(2 / 3, 2)
    assert m.price_median == 700
    assert m.price_p25 == 600 and m.price_p75 == 800


def test_gate_passes_on_strong_demand():
    products = [_p(1000, 500) for _ in range(20)]
    r = validate_demand("q", products, min_products=10, min_total_reviews=2000)
    assert r.stage == Stage.VALIDATE_DEMAND
    assert r.passed is True
    assert 0 < r.score <= 1
    assert r.evidence["total_reviews"] == 20000


def test_gate_fails_when_market_is_thin():
    r = validate_demand("q", [_p(10, 500) for _ in range(3)])
    assert r.passed is False


def test_gate_fails_on_weak_reviews():
    # enough products, but almost no buying activity
    r = validate_demand("q", [_p(1, 500) for _ in range(15)], min_total_reviews=2000)
    assert r.passed is False


def test_demand_score_empty_is_zero():
    assert demand_score(analyze_demand("q", [])) == 0.0
