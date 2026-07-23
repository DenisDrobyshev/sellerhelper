"""SQLAlchemy models for stored marketplace observations (the historization layer)."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ProductObservation(Base):
    """One product as seen in a search result at a point in time.

    Each crawl writes a fresh batch sharing one ``collected_at`` timestamp, so the
    table accumulates snapshots over time — which is what makes trend analysis
    (and the data moat) possible.
    """

    __tablename__ = "product_observations"

    id: Mapped[int] = mapped_column(primary_key=True)
    marketplace: Mapped[str] = mapped_column(String(32))
    query: Mapped[str] = mapped_column(String(256))
    external_id: Mapped[int] = mapped_column(Integer)
    root_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(512))
    brand: Mapped[str | None] = mapped_column(String(128), nullable=True)
    seller: Mapped[str | None] = mapped_column(String(128), nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    base_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    reviews: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position: Mapped[int] = mapped_column(Integer)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


Index("ix_obs_query_time", ProductObservation.query, ProductObservation.collected_at)


class WatchQuery(Base):
    """A query the collection scheduler crawls on each pass."""

    __tablename__ = "watch_queries"

    id: Mapped[int] = mapped_column(primary_key=True)
    query: Mapped[str] = mapped_column(String(256), unique=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
