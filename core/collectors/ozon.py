"""Ozon collector: a second marketplace, to test that the engine is marketplace-agnostic.

Ozon serves an anti-bot stub to automated browsers. Headless Chrome receives a
near-empty page (title "Похоже, нет соединения"), so live collection needs
residential proxies and stealth beyond this project's scope. The collector still
produces the same normalized ``Product`` objects as the Wildberries spider, and
the engine, storage and stages consume them without knowing the marketplace,
which is the property this connector exists to demonstrate.
"""

from __future__ import annotations

import re
import time
from urllib.parse import quote

from core.config import get_settings
from core.models.product import Product

_SEARCH = "https://www.ozon.ru/search/?from_global=true&text={q}"
_TILE = "a[href*='/product/']"
_ID_RE = re.compile(r"/product/[^/]*?-(\d+)/?")
_PRICE_RE = re.compile(r"(\d[\d\s ]{1,})₽")
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


def _price(text: str) -> float | None:
    match = _PRICE_RE.search((text or "").replace(" ", " "))
    if not match:
        return None
    digits = re.sub(r"[^\d]", "", match.group(1))
    return float(digits) if digits else None


class OzonCollector:
    """Selenium-driven Ozon search reader, mirroring the Wildberries spider."""

    marketplace = "ozon"

    def __init__(self, *, headless: bool | None = None) -> None:
        self._headless = get_settings().wb_headless if headless is None else headless
        self._driver = None

    def __enter__(self) -> "OzonCollector":
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        opts = Options()
        if self._headless:
            opts.add_argument("--headless=new")
        for arg in (
            "--window-size=1300,900",
            "--lang=ru-RU",
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--user-agent={_UA}",
        ):
            opts.add_argument(arg)
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        self._driver = webdriver.Chrome(options=opts)
        self._driver.set_page_load_timeout(45)
        return self

    def __exit__(self, *exc: object) -> None:
        if self._driver is not None:
            self._driver.quit()

    def search(self, query: str, *, limit: int = 100) -> list[Product]:
        driver = self._driver
        assert driver is not None, "use `with OzonCollector() as oz:`"
        driver.get(_SEARCH.format(q=quote(query)))
        time.sleep(4)
        for _ in range(4):
            driver.execute_script("window.scrollBy(0, 1500);")
            time.sleep(1.2)
        if len(driver.find_element("css selector", "body").text) < 400:
            return []  # Ozon served the anti-bot stub
        products: dict[int, Product] = {}
        for tile in driver.find_elements("css selector", _TILE):
            href = tile.get_attribute("href") or ""
            match = _ID_RE.search(href)
            if not match:
                continue
            ext_id = int(match.group(1))
            if ext_id in products:
                continue
            text = tile.text.strip()
            products[ext_id] = Product(
                marketplace=self.marketplace,
                external_id=ext_id,
                name=text.split("\n")[0][:120] if text else "",
                price=_price(text),
                url=href if href.startswith("http") else f"https://www.ozon.ru{href}",
            )
            if len(products) >= limit:
                break
        return list(products.values())


def crawl(query: str, *, limit: int = 100, headless: bool | None = None) -> list[Product]:
    """Open a browser and read an Ozon search page. Returns [] if Ozon blocks the bot."""
    with OzonCollector(headless=headless) as collector:
        return collector.search(query, limit=limit)


def _main() -> None:
    import sys

    query = " ".join(sys.argv[1:]) or "термокружка"
    print(f"[ozon] crawling {query!r} ...")
    try:
        products = crawl(query)
    except Exception as exc:
        print(f"[ozon] browser error: {type(exc).__name__}: {exc}")
        return
    if not products:
        print("[ozon] no products - Ozon served an anti-bot stub to the automated browser. "
              "Live collection needs residential proxies / stealth (out of scope).")
        return
    print(f"[ozon] collected {len(products)} products")
    for p in products[:10]:
        print(f"  {p.external_id}  {str(p.price) + ' RUB':>12}  {p.name[:50]}")


if __name__ == "__main__":
    _main()
