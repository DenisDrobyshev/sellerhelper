"""Stage 1 — Discover.

Turns a seed interest into concrete candidate niches, grounded in what people
actually sell on the marketplace rather than the model's imagination. It mines
the product names in a seed's search results for recurring sub-phrases
("термокружка" -> "автомобильная термокружка", "термокружка с трубочкой") and
attaches a price and demand read to each, so a budget can filter them.

Discover is a divergent stage — no gate. It hands you options to run through
Stage 2 (validate demand).
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from statistics import median

from core.models.product import Product

_STOP = {
    "для", "и", "с", "в", "на", "по", "из", "от", "до", "мл", "л", "шт", "см", "мм",
    "the", "for", "and", "of", "with",
}
_WORD = re.compile(r"[а-яёa-z0-9]+", re.IGNORECASE)
_MIN_PRODUCTS = 3


def _tokens(name: str) -> list[str]:
    return _WORD.findall(name.lower())


def _phrases(tokens: list[str]) -> set[str]:
    grams: set[str] = set()
    for n in (2, 3):
        for i in range(len(tokens) - n + 1):
            gram = tokens[i : i + n]
            if gram[0] in _STOP or gram[-1] in _STOP:
                continue
            if any(t.isdigit() for t in gram):
                continue
            grams.add(" ".join(gram))
    return grams


@dataclass
class CandidateNiche:
    query: str
    seed: str
    products: int
    price_median: float | None
    total_reviews: int


def discover_from_products(
    seed: str,
    products: list[Product],
    *,
    budget: float | None = None,
    top: int = 8,
) -> list[CandidateNiche]:
    """Mine candidate sub-niches from a seed's search results (pure, no network)."""
    seed_tokens = {t for t in _tokens(seed) if t not in _STOP and len(t) > 2}

    carriers: dict[str, list[Product]] = defaultdict(list)
    for product in products:
        for phrase in _phrases(_tokens(product.name)):
            carriers[phrase].append(product)

    def specialises_seed(phrase: str) -> bool:
        return not seed_tokens or bool(seed_tokens & set(phrase.split()))

    candidates = [
        phrase
        for phrase, carried in carriers.items()
        if len(carried) >= _MIN_PRODUCTS and phrase != seed.lower() and specialises_seed(phrase)
    ]
    if not candidates:  # nothing specialises the seed — fall back to any frequent phrase
        candidates = [
            phrase
            for phrase, carried in carriers.items()
            if len(carried) >= _MIN_PRODUCTS and phrase != seed.lower()
        ]

    niches: list[CandidateNiche] = []
    for phrase in candidates:
        carried = carriers[phrase]
        prices = [p.price for p in carried if p.price]
        price_median = round(median(prices), 2) if prices else None
        if budget is not None and price_median is not None and price_median > budget:
            continue
        niches.append(
            CandidateNiche(
                query=phrase,
                seed=seed,
                products=len(carried),
                price_median=price_median,
                total_reviews=sum(p.reviews or 0 for p in carried),
            )
        )

    niches.sort(key=lambda n: (n.products, n.total_reviews), reverse=True)
    return niches[:top]


def _print(seed: str, products: list[Product], budget: float | None) -> None:
    niches = discover_from_products(seed, products, budget=budget)
    print(f"\nStage 1 . Discover - seed {seed!r}  ({len(products)} products scanned)")
    if budget:
        print(f"  budget filter: unit price <= {budget:.0f} RUB")
    for n in niches:
        price = f"{n.price_median:.0f} RUB" if n.price_median else "-"
        print(f"   - {n.query:<32} x{n.products:<3} median {price:<10} reviews {n.total_reviews}")


def _demo(seed: str, budget: float | None) -> None:
    from core.collectors.wb_selenium import crawl

    products = crawl(seed)
    if not products:
        print(f"No products for {seed!r} - the crawl returned nothing.")
        return
    _print(seed, products, budget)


def _demo_db(seed: str, budget: float | None) -> None:
    from core.storage.repo import latest_snapshot

    products = latest_snapshot(seed)
    if not products:
        print(f"No stored snapshot for {seed!r}. Crawl first:")
        print(f'  python -m core.collectors.wb_selenium "{seed}"')
        return
    _print(seed, products, budget)


if __name__ == "__main__":
    import sys

    argv = sys.argv[1:]
    use_db = bool(argv) and argv[0] == "--db"
    if use_db:
        argv = argv[1:]
    budget = None
    if len(argv) >= 2 and argv[-1].replace(".", "", 1).isdigit():
        budget = float(argv[-1])
        argv = argv[:-1]
    seed = " ".join(argv) or "термокружка"
    (_demo_db if use_db else _demo)(seed, budget)
