# SellerCompass

> The open-source **AI co-founder for marketplace sellers**. Go from _"I want to sell online but don't know what"_ to a **validated first product** — grounded in live marketplace data, not guesswork.

![status](https://img.shields.io/badge/status-early--development-orange)
![license](https://img.shields.io/badge/license-MIT-blue)
![python](https://img.shields.io/badge/python-3.12-blue)

---

## The problem

Most people who want to start selling on a marketplace fail at step zero: **they pick the wrong product.** They either:

- stare at a blank business-plan template — and give up, or
- click an "AI business plan generator" that hands them a beautiful PDF full of invented numbers.

Both reward **fake progress** (a nice-looking plan) over **real progress** — evidence that someone will actually buy.

The tools that _do_ have real data (MPStats, Moneyplace, Jungle Scout, Helium 10) are **dashboards**: they dump numbers on you and assume you already know what to do with them. None of them take a beginner by the hand.

## What SellerCompass does differently

SellerCompass is **not a dashboard and not a plan generator**. It is a **guided, stage-gated pipeline** that walks a beginner from idea to a validated first product — and **won't let them advance until each step is backed by real data.**

Three principles:

1. **Evidence over opinion.** Every recommendation is grounded in live marketplace data (demand, competition, prices, reviews) — never the LLM's imagination.
2. **Gates, not a blank canvas.** You can't jump to "order inventory" until the demand and unit-economics gates pass.
3. **A co-founder, not a report.** The AI explains _why_ in plain language, flags risks, and tells you to **pivot or kill** when the data says so.

## The 5 stages (v0 — Wildberries)

| # | Stage | What happens | Gate to pass |
|---|-------|--------------|--------------|
| 1 | **Discover** | Budget + interests + goals → candidate niches | — |
| 2 | **Validate demand** | Real search volume, sales of top players, trend direction | Demand above threshold & not declining |
| 3 | **Size up competition** | Density, price bands, review strength; NLP over competitor reviews surfaces _unmet needs_ (your angle) | A real entry window exists |
| 4 | **Unit economics** | Purchase cost, logistics, marketplace fees, ads, price → per-unit margin, break-even, first-batch budget | Margin positive & realistic |
| 5 | **Decide** | Combined **Go / Pivot / Kill** verdict + concrete first-batch plan + launch checklist | — |

See [METHODOLOGY.md](METHODOLOGY.md) for the full spec of each gate.

## Open-core

- **Open (this repo, MIT):** the methodology engine, the marketplace connectors, and a fully self-hostable local version — bring your own LLM key and run it on your own machine.
- **Cloud (planned, hosted):** pre-collected live **and historical** marketplace data, zero setup, "log in and go." The **data infrastructure is the moat** — not the algorithm.

## Tech (planned)

Python · FastAPI · PostgreSQL · Redis · async collectors (httpx / Playwright) · LLM orchestration + RAG over market data · ML: demand forecasting, niche scoring, review NLP · Docker Compose one-command self-host.

See [ARCHITECTURE.md](ARCHITECTURE.md).

## Status

🚧 **Early development.** v0 targets **Wildberries**. Ozon and Amazon/Etsy are on the [roadmap](ROADMAP.md).

## Docs

- [METHODOLOGY.md](METHODOLOGY.md) — the stage-gate engine in detail
- [ARCHITECTURE.md](ARCHITECTURE.md) — stack, data pipeline, AI/ML layer
- [ROADMAP.md](ROADMAP.md) — where this is going

## License

[MIT](LICENSE) © 2026 Denis Drobyshev
