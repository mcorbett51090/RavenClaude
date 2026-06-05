# Small-firm practice KPI glossary

The metrics a small legal practice is judged on — formulas, the misreads, and where a figure needs a `[verify-at-use]` / `[unverified]` mark.

## Economic metrics

Realization (collected ÷ standard value), billed-vs-collected gap, write-down/write-off rate, collected revenue per attorney. Realization is the master number (§3 #1).

## Capacity metrics

Billable-hour utilization, non-billable/admin load, matters per attorney (§3 #5).

## Intake & A/R metrics

Conflict/decline rate, matter fit, A/R aging, collection cycle (§3 #2, #7).

---

## The realization cascade (cited benchmarks)

The three rates compound — read any one without the others and you misdiagnose the leak. Each is a **ratio**, and the product is what the lawyer actually banks.

| Metric | Formula | Clio 2025 average | Read |
|---|---|---|---|
| **Utilization** | billable hours ÷ available hours | ~38% (~3.0 billable hrs / 8-hr day) | The biggest leak — most of the day isn't captured as billable |
| **Realization** | billed value ÷ standard value (after write-downs) | ~88% | A write-down problem is a billing-narrative / scope problem, rarely a rate problem |
| **Collection** | collected ÷ billed (after write-offs) | ~93% | A collection problem is an A/R / engagement-terms problem |
| **Net effect** | utilization × realization × collection | ~2.4 of 8 hrs banked | The "busy but broke" arithmetic in one line |

Benchmarks are aggregate and move year to year — `[verify-at-use]`; calibrate to the firm's own waterfall, never substitute the benchmark for the firm's actual numbers (§3 #8). Source: [Clio — 2025 Legal Trends benchmarks](https://www.clio.com/resources/legal-trends/benchmarks/), retrieved 2026-06-05.

## Lockup, revenue & lockup days (Clio 2025)

| Metric | Value | Note |
|---|---|---|
| Realization lockup (median) | ~43 days | Time from work done to invoice issued |
| Collection lockup (median) | ~32 days | Time from invoice to payment |
| Total lockup (median) | ~93 days | A/R is part of the matter, not after it (§3 #7) |
| Billable revenue / lawyer — **solo** | ~$83,219 | Per the 2025 solo & small-firm report |
| Billable revenue / lawyer — **small firm (2–4)** | ~$156,963 | Per the 2025 solo & small-firm report |

Source: existing [`legal-practice-context.md`](legal-practice-context.md) (Clio 2025, retrieved 2026-06-04) — figures restated here for the glossary; `[verify-at-use]`.

## The Rule of Thirds (matter / attorney profitability sanity check)

A small-firm profitability heuristic: gross revenue splits roughly into three thirds — **~1/3 compensation** (attorney + billable-staff salary, benefits, payroll tax), **~1/3 overhead** (rent, tech, marketing, insurance, non-billable staff), **~1/3 profit**. The practical hiring threshold: a billable employee should generate **≥ 3× their fully-loaded cost of employment** in collected revenue (a lawyer costing ~$150k → bill/collect ~$450k).

**Caveat (cited):** it is a guideline, not a commandment — industry data shows overhead commonly runs **45–50%** of revenue in practice, so many firms sit below the 33% profit target; intentional deviations (lower overhead → higher comp, or higher marketing during growth) are fine, accidental ones are the warning sign. `[verify-at-use]`. Sources: [LeanLaw — Rule of Thirds](https://www.leanlaw.co/blog/the-rule-of-thirds-a-simple-framework-for-allocating-law-firm-revenue/), [CARET Legal — calculating the Rule of Thirds](https://caretlegal.com/blog/simplifying-your-law-firms-rule-of-thirds-calculation/), retrieved 2026-06-05.

## Trust-accounting controls (not a KPI — a hard guardrail)

Not a performance metric but the control every small-firm scorecard should confirm is **green/red**, not optimize: a **monthly three-way reconciliation** (bank statement balance = trust book balance = sum of all client ledgers) and a complete-records retention discipline (ABA Model Rule 1.15 floor: 5 years post-representation; **state rules vary and several are tightening to a 30-day cadence + mandatory three-way by July 1 2026** — `[verify-at-use]`). See [`legal-intake-and-trust-decision-trees.md`](legal-intake-and-trust-decision-trees.md). Trust/ethics calls route to the attorney + state bar rules (§3 #6).

## Sourcing note

Figures in this file are dated and cited where a public source exists; figures from the author's domain knowledge are marked `[unverified — training knowledge]` or `[verify-at-use]` at point of use. State-specific ethics/trust rules are **always** `[verify-at-use]`. Validate against a primary source before putting any figure in a client deliverable (§3 cite-or-mark rule).
