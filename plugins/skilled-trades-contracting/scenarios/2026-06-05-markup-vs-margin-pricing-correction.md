---
scenario_id: 2026-06-05-markup-vs-margin-pricing-correction
contributed_at: 2026-06-05
plugin: skilled-trades-contracting
product: pricing
product_version: "n/a"
scope: likely-general
tags: [markup, margin, pricing, estimating, flat-rate]
confidence: medium
reviewed: false
---

## Problem

An electrical contractor believed it was pricing every job for a "35% margin" and could not understand why the P&L showed gross margin closer to 26%. The owner was adding a **35% markup** to cost and calling it a "35% margin" — the single most common contractor pricing error. Every job was structurally underpriced by ~9 margin points before a single dollar of cost overrun.

## Context

- Trade: electrical, residential service + small commercial, flat-rate book on service, T&M-ish estimating on projects.
- Constraint: the flat-rate book and the estimating spreadsheet both applied a fixed percentage to cost and *labeled the result "margin"* — so the error was baked into every price, not a one-off.
- The owner reasoned "I add 35%, so I keep 35%." Markup is profit / **cost**; margin is profit / **price** — they are only equal at zero. A 35% markup yields a 25.9% margin.

## Attempts

- Tried: demonstrated the arithmetic before touching the book — `markup` mode of [`../scripts/trades_calc.py`](../scripts/trades_calc.py) showed a 35% markup yields a **25.9% margin**, and that **hitting** a 35% margin requires a **53.8% markup**. Outcome: the owner saw the ~9-point leak was definitional, not a discounting problem.
- Tried: rebuilt the flat-rate book and estimating template to compute price from the **target margin** (`price = cost / (1 − margin)`) rather than a markup-equals-margin shortcut. Outcome: prices rose to actually deliver the intended margin without changing the target.
- Tried: cross-checked the corrected prices against trade gross-margin ranges so the target itself was sane for the segment — specialty trades (electrical/HVAC) commonly land **~15–25%** gross at the GC-comparison level, while service/install electrical work can run materially higher (lower material-to-labor ratio) [verify-at-use]. Outcome: confirmed the target was reasonable and the prices weren't out of market.

## Resolution

The "missing margin" was a **markup-vs-margin confusion**, not weak pricing discipline or excess discounting. Converting the book and template to price from the target margin recovered the intended points across every job at once. The lesson generalizes: a markup table must be **derived from the margin you actually want**, never set equal to it.

**Action for the next consultant hitting this pattern:** when a contractor's realized margin sits a predictable few points below target on *every* job, suspect markup-vs-margin confusion before scope or efficiency. Confirm with `trades_calc.py markup`, then rebuild the price = cost / (1 − margin) into the flat-rate book and estimating template. See [`../knowledge/trades-markup-vs-margin-decision-tree.md`](../knowledge/trades-markup-vs-margin-decision-tree.md) and §3 #2 / #5.

**Sources (retrieved 2026-06-05):**
- Procore — *Construction Markup vs Profit Margin* (the markup ≠ margin trap, formulas): https://www.procore.com/library/construction-markup-and-profit-margin
- Buildern — *Construction Profit Margin vs. Markup* (20% markup → 16.7% margin worked example): https://buildern.com/resources/blog/construction-profit-margin-vs-markup/
- Siana — *General Contractor Profit Margin: 2026 Industry Data & Benchmarks* (specialty-trade gross-margin ranges): https://www.sianamarketing.com/resources/general-contractor-profit-margin

Margin ranges are segment- and trade-dependent; treat any specific number as `[verify-at-use]` and validate against the contractor's actual P&L (§3 #8).
