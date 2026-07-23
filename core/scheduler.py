"""Periodic collection.

Crawl every query on the watchlist and store a snapshot of each, then exit. Run
this on a fixed schedule (cron, or Windows Task Scheduler); each pass appends a
timestamped snapshot, which is what gives Stage 2's trend a real interval to
measure over.

    python -m core.scheduler --add "термокружка"     # register a query
    python -m core.scheduler --list                    # show the watchlist
    python -m core.scheduler --remove "термокружка"   # unregister a query
    python -m core.scheduler                            # crawl every watched query once
"""

from __future__ import annotations

import sys

from core.storage.repo import add_watch, list_watch, remove_watch, save_snapshot


def collect_once(queries: list[str] | None = None) -> dict[str, int]:
    """Crawl each query once and store a snapshot. Returns products saved per query."""
    from core.collectors.wb_selenium import crawl

    queries = list_watch() if queries is None else queries
    results: dict[str, int] = {}
    for query in queries:
        try:
            products = crawl(query)
        except Exception as exc:
            print(f"[scheduler] {query!r}: crawl failed ({type(exc).__name__})")
            results[query] = 0
            continue
        saved = save_snapshot(query, products) if products else 0
        print(f"[scheduler] {query!r}: {saved} products")
        results[query] = saved
    return results


def _main() -> None:
    args = sys.argv[1:]
    if args and args[0] == "--add":
        query = " ".join(args[1:])
        print(f"added {query!r}" if add_watch(query) else f"already watching {query!r}")
    elif args and args[0] == "--remove":
        query = " ".join(args[1:])
        print(f"removed {query!r}" if remove_watch(query) else f"not on the watchlist: {query!r}")
    elif args and args[0] == "--list":
        watched = list_watch()
        print("\n".join(watched) if watched else "(watchlist is empty)")
    else:
        saved = collect_once()
        print(f"[scheduler] done: {len(saved)} queries, {sum(saved.values())} products")


if __name__ == "__main__":
    _main()
