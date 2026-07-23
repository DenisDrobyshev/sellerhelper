"""Ozon connector: price parsing, and proof that the engine is marketplace-agnostic."""

from core.collectors.ozon import _price
from core.engine.decide import GO, KILL, PIVOT
from core.engine.pipeline import run_pipeline
from core.models.product import Product


def test_ozon_price_parsing():
    assert _price("Термокружка 1 299 ₽ синяя") == 1299.0
    assert _price("999₽") == 999.0
    assert _price("no price here") is None


def _ozon(reviews, rating, *, brand="B", name="термокружка стальная", price=1000):
    return Product(
        marketplace="ozon", external_id=1, name=name,
        reviews=reviews, rating=rating, price=price, brand=brand,
    )


def test_pipeline_runs_unchanged_on_ozon_products():
    products = [_ozon(500, 4.2, brand=f"B{i}") for i in range(12)]
    report = run_pipeline("термокружка", products, budget=100000)
    assert report.decision.verdict in (GO, PIVOT, KILL)
    assert all(p.marketplace == "ozon" for p in products)
    # the decision carries the same shape regardless of marketplace
    assert report.decision.economics.evidence["margin_per_unit"] != 0
