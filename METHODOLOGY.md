# Methodology — the stage-gate engine

SellerCompass's core is not the AI chat. It is a **state machine** with five stages. Each stage has:

- **inputs** it consumes,
- **data** it pulls from the live marketplace,
- **outputs** it produces,
- a **gate** — an explicit, data-driven pass/fail check. You cannot advance while a gate fails.

This is what makes SellerCompass honest: it refuses to let you feel productive without evidence.

```
[Discover] -> [Validate demand] -> [Size up competition] -> [Unit economics] -> [Decide]
     |               | gate               | gate                  | gate            |
  candidates    demand proven        entry window          margin proven      Go/Pivot/Kill
```

---

## Stage 1 — Discover

**Goal:** turn a vague wish into a short list of concrete candidate niches.

- **Inputs:** budget for the first batch, interests / domains the user knows, goal (side income vs. main business), risk appetite.
- **Data:** top-level category demand and dynamics on the marketplace.
- **Output:** 5–10 candidate niches, each with a one-line rationale.
- **Gate:** none (divergent stage — we _want_ options here).

## Stage 2 — Validate demand

**Goal:** prove that people actually want this, before spending a rouble.

- **Inputs:** candidate niches from Stage 1.
- **Data:** search-query volume, estimated sales of the top sellers, month-over-month trend, seasonality.
- **Output:** a demand score + trend label (growing / flat / declining) per niche.
- **Gate:** demand is **above the minimum threshold** AND **not in structural decline**. Declining niches are dropped or flagged.

## Stage 3 — Size up competition

**Goal:** find out whether there is room to enter — and what your angle would be.

- **Inputs:** niches that passed Stage 2.
- **Data:** number of active sellers, concentration (are the top 3 eating everything?), price bands, review counts and ratings of incumbents, and **the text of competitor reviews**.
- **AI/ML:** aspect-based NLP over competitor reviews to surface **recurring complaints** = unmet needs = your differentiation.
- **Output:** a competition-density index, a price corridor, and a list of concrete "customers are unhappy about X" openings.
- **Gate:** an **entry window exists** — competition is not saturated _and_ there is at least one credible way to be better.

## Stage 4 — Unit economics

**Goal:** prove the money works before ordering inventory.

- **Inputs:** the chosen niche + price corridor from Stage 3.
- **Data:** marketplace commission for the category, logistics/fulfilment fees, realistic ad cost per sale; purchase cost estimated (rough or user-supplied).
- **Output:** per-unit margin, break-even volume, and the **budget required for a viable first batch**.
- **Gate:** margin is **positive and realistic** given the price corridor and the user's budget. If the budget can't fund a viable batch, we say so.

## Stage 5 — Decide

**Goal:** a verdict you can act on tomorrow morning.

- **Inputs:** the passed/failed gates and scores from all previous stages.
- **Output:**
  - a combined **Go / Pivot / Kill** verdict with the reasoning,
  - a concrete **first-batch plan** (how many SKUs, how many units, at what budget),
  - a **launch checklist**.
- **Gate:** none — this is the exit.

---

## Design rules for the engine

- **Every gate cites its data.** No "trust me" verdicts — the number and its source are always shown.
- **Pivot is a first-class outcome.** Failing a gate is not an error; it routes the user back to the last viable branch (e.g. a different niche from Stage 1).
- **The LLM explains, the data decides.** Gates are computed from data. The LLM's job is to interpret intent, explain verdicts in plain language, and mine reviews — not to invent the numbers.
