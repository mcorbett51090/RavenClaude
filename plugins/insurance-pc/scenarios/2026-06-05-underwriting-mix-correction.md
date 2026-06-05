---
scenario_id: 2026-06-05-underwriting-mix-correction
contributed_at: 2026-06-05
plugin: insurance-pc
product: underwriting
product_version: "n/a"
scope: likely-general
tags: [line-of-business-mix, ncr, rate-adequacy, appetite, portfolio]
confidence: medium
reviewed: false
---

## Problem

An MGA's overall book ran a roughly break-even combined ratio, and leadership read that as "healthy." But premium had been growing fastest in a casualty line that was running well above 100, subsidized by a profitable property line — the average was hiding a mix shift toward the worst-performing line. The risk: growing the loss by celebrating the blended number while the underlying mix deteriorated.

## Context

- Segment: MGA / program business, commercial lines, in a soft-ish patch for the casualty line.
- Constraint: the portfolio result is a premium-weighted average of line results; a clean blended combined ratio can mask a mix shift toward higher-loss-ratio lines (§3 #6). The line growing fastest sets the book's future, not its past average.
- Public context for scale: general liability and commercial auto were the casualty lines running above a 100 net combined ratio in 2025, while homeowners (~88 NCR) and personal auto (~92 NCR) ran underwriting profits [verify-at-use] — a vivid reminder that line, not the average, tells the story.

## Attempts

- Tried: **decomposed the combined ratio by line** rather than reading the blended number (§3 #6). Outcome: the casualty line was well above 100 and the property line well below; the blend looked fine only because property was still the bigger book — but casualty was the one growing.
- Tried: **ran a rate-adequacy check on the deteriorating line** (§3 #2) instead of matching the competitor pricing that had won the growth. Outcome: the line's rate was inadequate to its trended loss ratio — the growth was bought with an underpriced rate, the §3 #2 anti-pattern (underwrite to the loss ratio, not the competitor's rate).
- Tried: **stripped cat per line** before judging each (§3 #4) so a cat-light year on the casualty line didn't flatter it. Outcome: the casualty line was attritionally unprofitable, not just cat-unlucky — a true appetite/pricing problem.

## Resolution

The correction was a **mix action plus a rate action**: tighten appetite and re-rate the casualty line to adequacy (accepting slower growth there), and protect/grow the profitable property line — rather than a blanket portfolio change. The deliverable was a per-line NCR table (attritional, net of reinsurance) with a rate indication on the deteriorating line, so the mix story was visible and the action was line-specific.

**Action for the next consultant hitting this pattern:** **never trust the blended combined ratio — decompose by line and watch where premium is GROWING.** A healthy average with growth concentrated in the worst line is a deteriorating book. Decompose NCR by line (§3 #6), strip cat per line (§3 #4), and run a rate-adequacy test on any line you're growing (§3 #2) — match the rate to the loss ratio, not the competitor. The [`../scripts/pc_calc.py`](../scripts/pc_calc.py) `rate-indication` mode computes the indicated change on the drifting line; `combined-ratio` does the per-line attritional/cat split. Pair with [`../knowledge/pc-decision-trees.md`](../knowledge/pc-decision-trees.md) "Which lines to grow/shrink".

**Sources (retrieved 2026-06-05):**
- III / Triple-I — strength in personal auto, pressure in GL lines (by-line NCR): https://www.iii.org/press-release/triple-i-milliman-2025-us-p-c-insurance-outlook-shows-strength-in-personal-auto-ongoing-pressure-in-general-liability-lines-071025
- Carrier Management — good times may not last; by-line detail: https://www.carriermanagement.com/news/2026/01/06/283094.htm
- CAS — Basic Ratemaking (loss-ratio method / rate adequacy): https://www.casact.org/sites/default/files/2021-07/Werner_Modlin_Basic_Ratemaking.pdf

Per-line NCR figures are recent-year industry datapoints, not hard rules — treat as `[verify-at-use]` and validate against the book's own line experience and accident year (§3 #8).
