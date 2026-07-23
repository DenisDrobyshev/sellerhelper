"""Tests for the full-pipeline orchestrator — pure logic, no network."""

from core.engine.decide import GO, PIVOT
from core.engine.pipeline import run_pipeline
from core.models.product import Product


def _p(reviews, rating, *, price=1000, brand="B", name="термокружка стальная"):
    return Product(
        marketplace="wildberries", external_id=1, name=name,
        reviews=reviews, rating=rating, price=price, brand=brand,
    )


def test_report_has_decision_and_candidates():
    products = [_p(500, 4.2, brand=f"B{i}") for i in range(12)]
    report = run_pipeline("термокружка", products, budget=100000)
    assert report.decision.verdict in (GO, PIVOT)
    assert report.candidates  # "термокружка стальная" recurs across the listings


def test_pipeline_pivots_on_saturated_market():
    products = [_p(100000, 4.2, brand="Giant")] + [_p(500, 4.2, brand=f"B{i}") for i in range(11)]
    report = run_pipeline("термокружка", products, budget=100000)
    assert report.decision.competition.passed is False
    assert report.decision.verdict == PIVOT
