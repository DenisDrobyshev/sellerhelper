"""Tests for Stage 1 (Discover) niche mining — pure logic, no network."""

from core.engine.discover import discover_from_products
from core.models.product import Product


def _p(name: str, reviews: int = 100, price: float = 500) -> Product:
    return Product(marketplace="wildberries", external_id=1, name=name, reviews=reviews, price=price)


def test_mines_subniches_that_specialise_the_seed():
    products = [
        _p("Автомобильная термокружка для кофе"),
        _p("Автомобильная термокружка туристическая"),
        _p("Автомобильная термокружка большая"),
        _p("Термокружка с трубочкой Stanley"),
        _p("Термокружка с трубочкой синяя"),
        _p("Термокружка с трубочкой 890 мл"),
        _p("Керамическая кружка для чая"),
    ]
    queries = [n.query for n in discover_from_products("термокружка", products, top=6)]
    assert "автомобильная термокружка" in queries
    assert "термокружка с трубочкой" in queries


def test_candidates_are_backed_by_enough_products():
    products = [_p(f"термокружка стальная {i}") for i in range(3)] + [_p("термокружка редкая одна")]
    niches = discover_from_products("термокружка", products)
    assert all(n.products >= 3 for n in niches)
    assert "термокружка редкая" not in [n.query for n in niches]


def test_budget_filters_out_expensive_niches():
    cheap = [_p(f"термокружка дешёвая {i}", price=300) for i in range(3)]
    pricey = [_p(f"термокружка премиум {i}", price=5000) for i in range(3)]
    niches = discover_from_products("термокружка", cheap + pricey, budget=1000)
    assert all(n.price_median is None or n.price_median <= 1000 for n in niches)
    assert "термокружка премиум" not in [n.query for n in niches]
