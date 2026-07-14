"""Unit tests for the Wildberries collector — normalization logic, no network.

The parsing is tested against the exact JSON shape observed from the live WB
search API, so these tests pin the contract even as the endpoint drifts.
"""

from core.collectors.wildberries import WildberriesCollector, _extract_price


def test_extract_price_from_sizes():
    raw = {"sizes": [{"price": {"basic": 250000, "product": 199000}}]}
    assert _extract_price(raw) == (1990.0, 2500.0)


def test_extract_price_legacy_fallback():
    raw = {"priceU": 300000, "salePriceU": 210000}
    assert _extract_price(raw) == (2100.0, 3000.0)


def test_extract_price_missing():
    assert _extract_price({}) == (None, None)


def test_normalize_maps_fields():
    wb = WildberriesCollector(client=object())  # constructor touches no network
    raw = {
        "id": 123,
        "root": 999,
        "brand": "Apple",
        "supplier": "ACME",
        "name": "Чехол для iPhone",
        "reviewRating": 4.8,
        "feedbacks": 1200,
        "sizes": [{"price": {"basic": 100000, "product": 90000}}],
    }
    p = wb._normalize(raw)

    assert p.marketplace == "wildberries"
    assert p.external_id == 123
    assert p.root_id == 999
    assert p.price == 900.0
    assert p.base_price == 1000.0
    assert p.rating == 4.8
    assert p.reviews == 1200
    assert "123" in p.url
