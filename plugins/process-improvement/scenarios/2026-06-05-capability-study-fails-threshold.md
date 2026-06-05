---
scenario_id: 2026-06-05-capability-study-fails-threshold
contributed_at: 2026-06-05
plugin: process-improvement
product: spc-capability
scope: likely-general
tags: [capability, cpk, centering, spread, spc]
confidence: medium
reviewed: false
---

## Problem

A precision-machining line had a customer-critical dimension with spec 9.0–11.0 mm. A capability study came back **Cpk ≈ 0.89** — below the 1.33 the customer's PPAP required — and the team's instinct was to "tighten the process" by buying a more precise (and expensive) tool. The ask was to confirm the diagnosis before the capital request.

## Context

- Sector: contract manufacturing, automotive tier-2; the dimension fed a downstream assembly with no rework path (a defect is scrap).
- Constraint: the customer's threshold was contractual (Cpk ≥ 1.33); a new tool was a 6-figure capital ask with a multi-month lead time.
- The team had run the capability study but had **not** first confirmed the process was in statistical control, and had not separated the centering question from the spread question.

## Attempts

- Tried: confirmed statistical **control** first (the §2 house rule — capability on an out-of-control process is meaningless). The I-MR chart showed no special-cause signals — the process was stable. Outcome: capability number is trustworthy; proceed to diagnose *why* it's low. `[ESTIMATE]` figures throughout — illustrative, not a real client's data.
- Tried: compared **Cp vs Cpk**. With mean 10.2 and within-sigma 0.30, Cp ≈ 1.11 but Cpk ≈ 0.89 (the capability calculator's `capability` mode reproduces this). The large Cp−Cpk gap said the spread *nearly* fits — the process is **off-center** (running high toward the USL), not too wide. Outcome: this is a **centering** problem, not a spread problem.
- Tried (the move that worked): re-centered the setpoint from ~10.2 toward 10.0 (the spec midpoint) — a free, same-day machine adjustment, no new tool. Re-ran the study: Cpk rose to ≈ 1.30, then a small variation-reduction tweak (a fixturing fix found via the root-cause tree) carried it past 1.33. Outcome: met the contractual threshold without the capital spend.

## Resolution

The low Cpk was a **centering miss masquerading as a spread problem**. "Improve capability" is not one action: a centering problem is a cheap setpoint change; a spread problem is an expensive variation-reduction project. Diagnosing *which* (via Cp-vs-Cpk) before spending deferred — and ultimately avoided — the six-figure tool purchase.

**Action for the next Black Belt hitting this pattern:** when a capability study fails its threshold, do **not** jump to "reduce variation" (or worse, buy precision). Traverse the **capability-study-came-back-low** tree in [`../knowledge/spc-response-decision-trees.md`](../knowledge/spc-response-decision-trees.md): confirm control first, then compare Cp to Cpk — if Cp is fine but Cpk is low, it's centering (cheap); only if Cp itself is low do you have a spread problem. Run the `capability` mode of [`../scripts/lss_calc.py`](../scripts/lss_calc.py) to see all four indices and the Cpk−Ppk gap at once. The capability **confidence interval** (is 1.30 *significantly* ≥ 1.33 given the sample?) routes to `applied-statistics` (CLAUDE.md §8) — a point estimate on the threshold line is not proof.

**Sources for facts cited:** Cp/Cpk formulas + the 1.33/1.67 thresholds — [Six Sigma Study Guide: Pp/Ppk/Cp/Cpk](https://sixsigmastudyguide.com/process-capability-pp-ppk-cp-cpk/) (retrieved 2026-06-05); the capability-vs-control house rule is in [`../knowledge/six-sigma-statistics-and-spc.md`](../knowledge/six-sigma-statistics-and-spc.md) §2. Figures are illustrative `[ESTIMATE]` for this scenario; validate against the line's actual data before a deliverable.
