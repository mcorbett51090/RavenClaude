---
scenario_id: 2026-06-05-peeking-early-stop-false-positive
contributed_at: 2026-06-05
plugin: experimentation-growth-engineering
product: experimentation
product_version: "n/a"
scope: likely-general
tags: [peeking, early-stopping, false-positive, fixed-horizon, sequential]
confidence: high
reviewed: false
---

## Problem

A growth team kept "winning" tests that didn't replicate. Their dashboard showed a live p-value, and the PM's habit was to ship the moment it crossed 0.05 — sometimes on day 2 of a planned 3-week test. Three "wins" in a quarter failed to move the topline metric after launch. The team's read was "our experiments are noisy"; the actual problem was the analysis regime.

## Context

- Fixed-horizon test design (pre-registered N + duration) but a real-time significance readout visible to decision-makers.
- ~15 experiments/quarter on a consumer funnel; baseline conversion ~4%.
- The platform showed a continuously-updating p-value with no correction for repeated looks.

## Attempts

- Tried: telling the PM "don't look early." Failed — the readout was right there, and stopping at first significance felt like moving fast. Behavioral asks without a mechanism don't hold.
- Tried: quantifying the inflation to make the cost concrete. Repeatedly testing a fixed-horizon experiment at a nominal alpha of 0.05 inflates the real false-positive rate well above 5% — peeking continuously can push the cumulative Type-I error toward ~20-30%+ depending on how often you look. That reframed "noisy experiments" as "we built a false-positive machine." `[verify-at-use — the exact inflation depends on the number/cadence of looks; route the precise figure to applied-statistics]`
- Tried (the move that worked): split the decision into two regimes and made the apparatus enforce whichever was chosen. For tests where early stopping has real value (risky change, fast learning), adopt a **sequential** method with always-valid / group-sequential boundaries (designed with `applied-statistics`) and expose only the valid stopping boundary in the UI. For everything else, **lock the readout until the pre-registered horizon** — the dashboard shows progress-to-N, not a live p-value.

## Resolution

The fix was structural, not exhortation: **the analysis regime is chosen up front and the apparatus hides the readout that enables the wrong move.** A fixed-horizon test's results are locked until the horizon; a sequential test exposes only a valid stopping boundary. After the change, the "wins that don't replicate" rate dropped because a fixed-horizon test could no longer be stopped at a random favorable peek.

**Action for the next engineer hitting this pattern:** if a team reports "our A/B wins don't replicate," check first whether a fixed-horizon test is being stopped early on a live p-value — that's the most common cause and it masquerades as noise. The mechanism fix is to lock the readout (fixed-horizon) or switch to a sequential design with `applied-statistics`; do not let a continuously-updating nominal p-value drive a stop. Use `experiment_calc.py sample-size` to set and pre-register the horizon. The "what is the valid stopping rule / always-valid p-value" math is `applied-statistics`' call, not ours (CLAUDE.md §3 #1, #4).

Cross-reference: complements the "Fixed-horizon or sequential test?" and "Can I trust this experiment result?" trees in [`../knowledge/experimentation-growth-engineering-decision-trees.md`](../knowledge/experimentation-growth-engineering-decision-trees.md), and [`../best-practices/no-peeking-pre-register.md`](../best-practices/no-peeking-pre-register.md) + [`../best-practices/sequential-vs-fixed-horizon.md`](../best-practices/sequential-vs-fixed-horizon.md).

**Sources (retrieved 2026-06-05):**
- Sequential testing / always-valid inference primers — https://www.statsig.com/blog/sample-ratio-mismatch (platform context); the peeking-inflation result is standard sequential-analysis theory — confirm the exact inflation figure with `applied-statistics` at use.
