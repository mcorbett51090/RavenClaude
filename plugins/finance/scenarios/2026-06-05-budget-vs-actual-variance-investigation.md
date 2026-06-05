---
scenario_id: 2026-06-05-budget-vs-actual-variance-investigation
contributed_at: 2026-06-05
plugin: finance
product: fpa
product_version: "n/a"
scope: likely-general
tags: [variance, budget-vs-actual, reconcile-before-narrate, pvm, materiality]
confidence: medium
---

## Problem

A monthly close landed gross margin ~310 bps below plan, and the CFO wanted a one-line explanation by the next morning's leadership meeting. The FP&A analyst's first instinct — and the COO's offered narrative — was "the forecast was too aggressive." That answer would have been written into the board commentary and quietly re-based next quarter's plan, papering over whatever actually moved.

## Context

- Segment: mid-market manufacturer, single reporting currency, multi-product.
- Constraint: the close had just locked; one inventory sub-ledger had **not** yet been reconciled to the GL when the variance first surfaced. A materiality threshold existed on paper ("explain ≥ $50K or ≥ 5%") but wasn't being applied consistently — the team was chasing a $9K freight variance while the margin gap sat unexplained.
- Pressure to narrate fast was pulling the team toward the *last* leaf of the triage tree (forecast was wrong) on the first pass.

## Attempts

- Tried: **reconcile before narrating** (§3 #3). Held the commentary until the inventory sub-ledger tied to the GL. Outcome: the recon surfaced an un-booked standard-cost revaluation — roughly a third of the gap was a cutoff/accounting item, not an operating miss. Narrating before the recon would have described noise.
- Tried: traversed the variance-root-cause triage tree top-to-bottom (RECON → TIMING → ONE-TIME → FX → PVM → DECISION → FORECAST) rather than pattern-matching. Single currency, so the FX leaf was skipped explicitly. Outcome: the residual, real operating variance routed to a **price/volume/mix bridge** because the line was multi-product.
- Tried: built the PVM bridge so the three effects summed exactly to the residual variance. Outcome: the operating piece was a **mix** shift (a lower-margin product line grew faster than plan), not a price cut or a volume miss — a fundamentally different conversation than "sales discounted."

## Resolution

The honest commentary was three sentences, not one: ~1/3 of the gap was a standard-cost revaluation booked late (a controller/cutoff item, reversing the run-rate read), and the operating remainder was an unfavorable product **mix** — higher growth in a structurally lower-margin line — with price and volume roughly on plan. The "forecast was too aggressive" story was wrong and would have masked both the cutoff item and a real mix signal the commercial team needed.

**Action for the next analyst hitting this pattern:** **reconcile before you narrate, and traverse the triage tree in order — "the forecast was wrong" is the last leaf, not the first.** Apply the materiality threshold so you spend the cycle on the margin gap, not the $9K freight line. When the line is multi-product, the operating residual almost always needs a PVM bridge that sums exactly to the total; a mix shift reads nothing like a price cut. Canonical references: [`../knowledge/variance-root-cause-triage.md`](../knowledge/variance-root-cause-triage.md) and the variance-decomposition tree in [`../knowledge/finance-decision-trees.md`](../knowledge/finance-decision-trees.md). The [`../scripts/finance_calc.py`](../scripts/finance_calc.py) `variance-bridge` mode does the PVM arithmetic.

**Sources (retrieved 2026-06-05):**
- Numeric — variance-analysis guide (materiality thresholds, dollar + percent): https://www.numeric.io/blog/variance-analysis-guide
- gSquared CFO — variance analysis, finding the story behind the numbers: https://www.gsquaredcfo.com/blog/variance-analysis

Materiality thresholds (5–10% major lines, 15–20% smaller, or a dollar floor ~$10K–$25K) are common ranges from the trade literature, not hard rules — treat as `[verify-at-use]` and calibrate to the entity's size and risk tolerance (§3 #5).
