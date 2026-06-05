---
scenario_id: 2026-06-05-menu-repriced-on-percentage
contributed_at: 2026-06-05
plugin: restaurant-operations
product: menu
product_version: "n/a"
scope: likely-general
tags: [menu-engineering, contribution-margin, pricing, plowhorse, mix]
confidence: medium
reviewed: false
---

## Problem

A fast-casual operator had been "fixing food cost" by chasing the food-cost **percentage** of each item — pushing every dish toward a target % and cutting or de-emphasizing anything above it. Food cost % looked fine on paper, but four-wall dollars weren't growing. The highest-margin-in-dollars items were being suppressed because their *percentage* looked unattractive next to cheap, low-dollar sides.

## Context

- Segment: fast-casual, 2 units, counter-service. Decent POS mix data (units sold per item) was available but unused for engineering.
- Constraint: the menu had never been run through the engineering matrix — items were judged one at a time on food-cost %, never on **contribution margin in dollars × popularity** (§3 #3, #5).
- The operator conflated "low food-cost %" with "high profit." A 22%-food-cost side can earn fewer absolute dollars than a 38%-food-cost entrée that guests actually order (§3 #5). Single-metric trap.

## Attempts

- Tried: built the **menu engineering matrix** (§3 #3, the engineer-the-menu skill) — every item placed on contribution-margin (price − plate cost, in dollars) vs popularity. Popularity threshold set with the standard rule: an item is "popular" if its menu-mix share is **≥ 70% of (1 ÷ number of items)** [verify-at-use]. Result: revealed several **plowhorses** (popular, low-margin) being run as loss leaders and two **puzzles** (high-margin, under-ordered) buried at the bottom of the menu.
- Tried: the four canonical moves — **protect stars, work the plowhorses (small price nudge or cost engineering, not a cut), promote puzzles (menu placement + server mention), remove/rework dogs** (§3 #3). Result: shifted mix toward the high-dollar-margin items without a broad price increase.
- Tried: re-priced **only** where the matrix justified it (plowhorses that could absorb a small lift), from the cost stack and value — never an across-the-board cut (§3 #3, the resist-the-price-cut discipline).

## Resolution

The problem was **engineering on the wrong axis** — food-cost % instead of contribution-margin dollars and popularity. Re-engineering the mix (promote puzzles, reposition plowhorses, protect stars, cut dogs) raised four-wall contribution dollars without a blanket price move. The percentage was never the goal; **dollars of margin per cover** was.

**Action for the next consultant hitting this pattern:** never re-price or cut a menu on food-cost % alone (§3 #5). Build the matrix on **contribution margin in dollars × popularity**, set the popularity bar at 70% of even-share, and apply the four moves. A price *cut* is rarely the lever that fixes margin (§3 #3) — moving the mix usually is.

**Sources (retrieved 2026-06-05):** matrix categories + the four strategic moves — Toast *Menu Engineering Matrix* (https://pos.toasttab.com/blog/on-the-line/menu-engineering-matrix); the contribution-margin definition (price − plate cost) — meez *Menu Engineering Matrix* (https://www.getmeez.com/blog/menu-engineering-matrix); the **70% × (1/N)** popularity threshold (Kasavana-Smith) — Apicbase *Restaurant Menu Engineering* (https://get.apicbase.com/restaurant-menu-engineering/). Treat any specific figure as `[ESTIMATE]`; validate the mix against the unit's actual POS data (§3 #8).
