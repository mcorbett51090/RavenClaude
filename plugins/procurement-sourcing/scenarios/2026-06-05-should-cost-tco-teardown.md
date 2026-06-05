---
scenario_id: 2026-06-05-should-cost-tco-teardown
contributed_at: 2026-06-05
plugin: procurement-sourcing
product: sourcing
product_version: "n/a"
scope: likely-general
tags: [should-cost, tco, unit-price, negotiation, leverage]
confidence: medium
reviewed: false
---

## Problem

An engineered single-source component had resisted every benchmarking attempt — there was no comparable market price to anchor a negotiation, and the incumbent knew it. The team was stuck asking for "a better price" with no leverage, and an apparent low-price quote from an alternate supplier looked attractive until the total cost was examined. Two failures were tangled together: **no negotiating leverage** (no should-cost) and a **unit-price illusion** (the cheap quote wasn't cheap on TCO).

## Context

- Segment: direct material, engineered/spec-locked part, effectively single-source — the leverage quadrant's competitive-auction play was unavailable, so benchmarking (market-price comparison) gave almost no leverage (§3 #6).
- Constraint: the alternate supplier's lower unit price carried higher freight, a higher defect rate, and a one-time switching/qualification cost — none of which showed in the quoted price (§3 #2: source on TCO, not unit price).
- The team conflated "lowest quoted price" with "lowest cost" and "benchmark" with "leverage." For an engineered single-source item, neither holds.

## Attempts

- Tried: built a **should-cost** model — materials + labor + overhead + margin built up from the part's bill of materials and process — instead of a market benchmark. For an engineered single-source item, should-cost is the only credible leverage: it lets you argue the *cost structure*, not a price the supplier knows isn't comparable. Outcome: a fact-based negotiating position the incumbent had to engage with.
- Tried: ran `scripts/sourcing_calc.py tco` on the incumbent vs the alternate, loading the full stack — landed unit (price + freight), quality/defect cost, inventory carry, and the one-time switching/qualification cost. Outcome: the "cheaper" alternate **lost on TCO** once defect and switching cost were included; the unit-price savings was an illusion. The calculator's own unit-price-trap note flagged it.
- Tried: used the should-cost gap to negotiate the incumbent down rather than switching for a phantom saving. Outcome: a real, durable rate reduction without the switching risk.

## Resolution

For an engineered single-source item, **should-cost beat benchmarking for leverage** and **TCO beat unit price for the award decision**. The alternate's lower sticker price was erased by quality and switching cost; the durable win was a should-cost-anchored negotiation with the incumbent. Two house opinions did the work: build the cost up (§3 #6), and source on total cost (§3 #2).

**Action for the next consultant hitting this pattern:** when a category is engineered / single-source and benchmarking gives no leverage, **build a should-cost model** (materials + labor + overhead + margin) — it is the leverage benchmarking can't provide (§3 #6). Never award on unit price — run the full **TCO** (freight + quality + carry + switching) with `scripts/sourcing_calc.py tco`; a low unit price that loses on TCO is a loss in disguise (§3 #2). Use the should-cost gap to negotiate the incumbent before switching for a saving that switching cost may erase.

**Sources (retrieved 2026-06-05):** TCO components incl. switching/quality + should-cost as the validation complement — https://simfoni.com/glossary/total-cost-of-ownership-tco/ ; https://www.cips.org/intelligence-hub/finance/total-cost-of-ownership ; https://www.purchasing-procurement-center.com/total-cost-of-ownership.html . Should-cost vs benchmarking leverage for engineered items is standard sourcing practice; cost-structure figures are client-specific — treat any number as `[ESTIMATE]` and validate against the part's actual BOM and the client's freight/defect data (§3 #8).
