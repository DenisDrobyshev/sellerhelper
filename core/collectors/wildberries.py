"""Wildberries public-catalog collector.

Wildberries exposes an unauthenticated JSON search API — the same public surface
that market-research tools rely on. It is also the hard part of the product: WB
aggressively rate-limits datacenter IPs (HTTP 429). This collector therefore
ships with polite rate limiting, exponential backoff on 429, and optional proxy
support. Run it from a residential / RU network, or set `WB_PROXY_URL`.

Smoke test:  python -m core.collectors.wildberries "чехол для iphone"
"""

from __future__ import annotations

import asyncio
import sys

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from core.collectors.base import MarketplaceCollector
from core.config import get_settings
from core.models.product import Product

SEARCH_URL = "https://search.wb.ru/exactmatch/ru/common/{version}/search"
FEEDBACKS_HOSTS = ("feedbacks1.wb.ru", "feedbacks2.wb.ru")


def _is_rate_limited(exc: BaseException) -> bool:
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429


def _kopecks(value: int | None) -> float | None:
    """WB returns prices in kopecks; convert to rubles."""
    return round(value / 100, 2) if value else None


def _extract_price(raw: dict) -> tuple[float | None, float | None]:
    """Return (final_price, base_price) in rubles, robust to WB schema drift.

    Newer endpoints nest prices under ``sizes[].price``; older ones expose
    top-level ``priceU`` / ``salePriceU``. We handle both.
    """
    sizes = raw.get("sizes") or []
    if sizes and isinstance(sizes[0], dict):
        price = sizes[0].get("price") or {}
        final = _kopecks(price.get("product") or price.get("total"))
        basic = _kopecks(price.get("basic"))
        if final or basic:
            return final or basic, basic or final
    return _kopecks(raw.get("salePriceU")), _kopecks(raw.get("priceU"))


class WildberriesCollector(MarketplaceCollector):
    marketplace = "wildberries"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._settings = get_settings()
        self._client = client
        self._owns_client = client is None
        rps = self._settings.wb_requests_per_second
        self._min_interval = 1 / rps if rps > 0 else 0.0
        self._last_request = 0.0

    async def __aenter__(self) -> "WildberriesCollector":
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=25,
                proxy=self._settings.wb_proxy_url or None,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
                    ),
                    "Accept": "*/*",
                    "Accept-Language": "ru-RU,ru;q=0.9",
                },
            )
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    async def _throttle(self) -> None:
        if not self._min_interval:
            return
        loop = asyncio.get_event_loop()
        wait = self._min_interval - (loop.time() - self._last_request)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_request = loop.time()

    @retry(
        retry=retry_if_exception(_is_rate_limited),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _get(self, url: str, params: dict | None = None) -> dict:
        assert self._client is not None, "use `async with WildberriesCollector()`"
        await self._throttle()
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def search(self, query: str, *, limit: int = 100) -> list[Product]:
        url = SEARCH_URL.format(version=self._settings.wb_search_version)
        params = {
            "appType": 1,
            "curr": "rub",
            "dest": self._settings.wb_dest,
            "resultset": "catalog",
            "sort": "popular",
            "spp": 30,
            "lang": "ru",
            "query": query,
        }
        payload = await self._get(url, params)
        raw_products = (payload.get("data") or {}).get("products") or []
        return [self._normalize(p) for p in raw_products[:limit]]

    async def reviews(self, root_id: int, *, limit: int = 100) -> list[str]:
        """Fetch recent review texts for a product group (WB imtId / ``root``)."""
        for host in FEEDBACKS_HOSTS:
            try:
                data = await self._get(f"https://{host}/feedbacks/v1/{root_id}")
            except httpx.HTTPStatusError:
                continue
            feedbacks = data.get("feedbacks") or []
            texts = [f["text"].strip() for f in feedbacks if f.get("text")]
            if texts:
                return texts[:limit]
        return []

    def _normalize(self, raw: dict) -> Product:
        price, base_price = _extract_price(raw)
        ext_id = raw.get("id")
        return Product(
            marketplace=self.marketplace,
            external_id=ext_id,
            root_id=raw.get("root"),
            name=raw.get("name", ""),
            brand=raw.get("brand"),
            seller=raw.get("supplier"),
            price=price,
            base_price=base_price,
            rating=raw.get("reviewRating") or raw.get("rating"),
            reviews=raw.get("feedbacks"),
            url=f"https://www.wildberries.ru/catalog/{ext_id}/detail.aspx" if ext_id else None,
        )


async def _demo(query: str) -> None:
    async with WildberriesCollector() as wb:
        products = await wb.search(query, limit=10)
    print(f"'{query}': {len(products)} products\n")
    for p in products:
        price = f"{p.price:,.0f} RUB" if p.price else "—"
        print(f"  {price:>12}  *{p.rating or '-'} ({p.reviews or 0:>5})  {p.brand or ''} — {p.name[:55]}")


if __name__ == "__main__":
    asyncio.run(_demo(" ".join(sys.argv[1:]) or "чехол для iphone"))
