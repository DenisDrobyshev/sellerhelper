"""Collector interface shared by every marketplace connector."""

from abc import ABC, abstractmethod

from core.models.product import Product


class MarketplaceCollector(ABC):
    marketplace: str

    @abstractmethod
    async def search(self, query: str, *, limit: int = 100) -> list[Product]:
        """Return products matching `query`, normalized to `Product`."""
        raise NotImplementedError
