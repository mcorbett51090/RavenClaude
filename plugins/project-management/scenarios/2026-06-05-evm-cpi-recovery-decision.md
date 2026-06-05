---
scenario_id: 2026-06-05-evm-cpi-recovery-decision
contributed_at: 2026-06-05
plugin: project-management
product: delivery-predictive
product_version: "n/a"
scope: likely-general
tags: [earned-value, cpi, eac, tcpi, recovery, contingency]
confidence: medium
reviewed: false
---

## Problem

At roughly the 30% mark of a fixed-budget delivery, the CPI had settled at **~0.83** (over budget) and the sponsor wanted to know whether the team could "just make it up" over the back two-thirds, or whether more budget was needed. The PM had been answering "we'll tighten up" for a few weeks. The ask was to replace the hope with an arithmetic answer: can this project still land on its original budget, and if not, by how much will it overrun?

## Context

- Track: predictive, fixed budget-at-completion (BAC) of ~$1.0M `[ESTIMATE — illustrative]`, contingency reserve of ~8% held by the PM within delegation.
- Constraint: the sponsor's tolerance was a single-digit-percent overrun; anything larger needed a board-level funding decision, not a PM call.
- Past the ~20–25% mark, CPI tends to be **stable** — it rarely improves dramatically without a structural change — so "we'll catch up" needed to clear a high bar of evidence.

## Attempts

- Tried: computed the EAC variants (the `evm` mode of `scripts/evm_calc.py`). With CPI ~0.83 and the current trend continuing, **EAC1 = BAC / CPI ≈ $1.20M** — a ~20% overrun. Outcome: the "we'll catch up" answer was quantitatively implausible at the BAC tolerance.
- Tried: computed **TCPI = (BAC − EV) / (BAC − AC)** — the cost efficiency the *remaining* work would have to hit to still land on BAC. It came out **>1.10**, i.e. the team would have to run materially *more* efficiently for the rest of the project than it ever had — which the EVM literature flags as "very challenging", and above ~1.20 as effectively unrecoverable. Outcome: established that recovery-to-original-budget was not realistic.
- Tried (the move that worked): routed the variance through the [`../knowledge/pm-recover-vs-escalate-slip-decision-tree.md`](../knowledge/pm-recover-vs-escalate-slip-decision-tree.md). The overrun exceeded both contingency and PM authority, so the branch was **escalate** — but as a *packaged steering decision* (not an emergency), with EAC/VAC/TCPI, two recovery options (de-scope to a lower BAC vs sponsor-funded extension), and a recommendation, with the sponsor pre-wired. Outcome: a conscious sponsor decision (a modest de-scope plus a small funded extension) replaced a slow-motion silent overrun.

## Resolution

The CPI was the early-warning the project needed: at ~30% complete a CPI of ~0.83 forecast a ~20% overrun, and TCPI proved that "catching up" would require an implausible efficiency jump. The right move was not to promise recovery but to **package the forecast as a steering decision** with options — turning an arithmetic certainty into a governed choice.

**Action for the next PM hitting this pattern:** once past ~20–25% complete, **trust the CPI** — compute EAC1 (BAC/CPI) and TCPI before promising recovery. A TCPI above ~1.10 means recovery-to-budget is very challenging; above ~1.20, treat it as unrecoverable and stop promising it. Take the forecast to the sponsor as a packaged decision with options via the recover-vs-escalate tree, not as a surprise. Earned value tells two stories — cost (CPI) and schedule (SPI) — read both (`../best-practices/earned-value-tells-two-stories.md`).

**Sources for framings cited:** EVM formulas web-verified 2026-06-05 — EAC = BAC / CPI (current trend), TCPI = (BAC − EV) / (BAC − AC), with TCPI > 1.10 "very challenging" and > 1.20 effectively unrecoverable: [ShriLearning EVM formulas guide](https://shrilearning.com/evm-formulas-pmp/), [PM Study Circle TCPI](https://pmstudycircle.com/to-complete-performance-index-tcpi-in-project-cost-management/), [PMCLounge cost formulas](https://www.pmclounge.com/all-pmp-cost-management-formulas/). The CPI-stability-after-~20% observation is a widely-cited EVM heuristic [verify-at-use]. BAC/CPI figures are illustrative for this scenario; validate against the project's actual baseline before a deliverable.
