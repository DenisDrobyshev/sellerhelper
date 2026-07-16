"""Persistence for marketplace observations — save and read back snapshots."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from core.models.product import Product
from core.storage.db import get_engine
from core.storage.models import ProductObservation


def save_snapshot(
    query: str,
    products: list[Product],
    *,
    engine: Engine | None = None,
    collected_at: datetime | None = None,
) -> int:
    """Persist a ranked snapshot of products for a query. Returns rows written."""
    engine = engine or get_engine()
    ts = collected_at or datetime.now(timezone.utc)
    with Session(engine) as session:
        session.add_all(
            ProductObservation(
                marketplace=p.marketplace,
                query=query,
                external_id=p.external_id,
                root_id=p.root_id,
                name=p.name,
                brand=p.brand,
                seller=p.seller,
                price=p.price,
                base_price=p.base_price,
                rating=p.rating,
                reviews=p.reviews,
                position=pos,
                collected_at=ts,
            )
            for pos, p in enumerate(products, start=1)
        )
        session.commit()
    return len(products)


def latest_snapshot(query: str, *, engine: Engine | None = None) -> list[Product]:
    """Return the most recent stored snapshot for a query, ranked by position."""
    engine = engine or get_engine()
    with Session(engine) as session:
        latest = session.scalar(
            select(func.max(ProductObservation.collected_at)).where(
                ProductObservation.query == query
            )
        )
        if latest is None:
            return []
        rows = session.scalars(
            select(ProductObservation)
            .where(
                ProductObservation.query == query,
                ProductObservation.collected_at == latest,
            )
            .order_by(ProductObservation.position)
        ).all()
    return [
        Product(
            marketplace=r.marketplace,
            external_id=r.external_id,
            root_id=r.root_id,
            name=r.name,
            brand=r.brand,
            seller=r.seller,
            price=r.price,
            base_price=r.base_price,
            rating=r.rating,
            reviews=r.reviews,
        )
        for r in rows
    ]


def snapshot_totals_over_time(
    query: str, *, engine: Engine | None = None
) -> list[tuple[datetime, int]]:
    """Return (collected_at, total_reviews) per snapshot, oldest first — for trend."""
    engine = engine or get_engine()
    with Session(engine) as session:
        rows = session.execute(
            select(
                ProductObservation.collected_at,
                func.coalesce(func.sum(ProductObservation.reviews), 0),
            )
            .where(ProductObservation.query == query)
            .group_by(ProductObservation.collected_at)
            .order_by(ProductObservation.collected_at)
        ).all()
    return [(row[0], int(row[1])) for row in rows]
