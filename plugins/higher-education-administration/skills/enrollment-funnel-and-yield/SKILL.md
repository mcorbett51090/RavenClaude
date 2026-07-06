---
name: enrollment-funnel-and-yield
description: "Model the enrollment funnel stage-by-stage (inquiry->apply->admit->yield->melt), compute yield and melt, and find the leaking stage before spending at the top of the funnel. Every benchmark carries a definition + retrieval date + verify-at-use; cohort-level only, no student PII."
---

# Enrollment Funnel & Yield

The class size everyone quotes is an **output**. This skill decomposes it into the stage rates that actually produce it, so you move the stage that's leaking instead of buying more inquiries by reflex.

> **Advisory, not compliance advice.** Funnel benchmarks and yield/melt rates are volatile and institution-specific. Every specific here is `[verify-at-use]` against the institution's own IR definitions. No student PII — model cohorts, never individual records.

## The funnel

| Stage | Definition (attach the institution's own) | The rate it feeds |
|---|---|---|
| Inquiry | A prospective student who has expressed interest | Apply rate = applications / inquiries |
| Application | A submitted, complete application | Admit rate = admits / applications |
| Admit | An offer of admission extended | Yield = deposits / admits |
| Deposit / commit | An enrolled-intent (deposit or equivalent) | Melt = (deposits − census enrollments) / deposits |
| Census enrollment | Enrolled at the official count date | The class |

**The rule:** a target class = inquiries × apply rate × admit rate × yield × (1 − melt). Change the term that's actually low, not the one that's easiest to buy.

## The math that matters

- **Yield** = deposits ÷ admits. The single most-watched — and most-defendable — funnel rate.
- **Melt** = the share of deposits that never enroll (summer melt for a fall class). Cheap to defend, expensive to replace.
- **Marginal net student** = the net tuition revenue of one more enrolled student at the current discount scenario — the number that decides whether a lever is worth pulling (see [`../financial-aid-and-discount-rate/SKILL.md`](../financial-aid-and-discount-rate/SKILL.md)).

## Metrics table

| Metric | What it tells you | Watch for |
|---|---|---|
| Apply rate | Top-funnel interest quality | High inquiries + low apply = weak fit or friction |
| Admit rate | Selectivity / class-shaping | Rising admit rate propping up a soft funnel |
| Yield | Competitiveness of the offer | A yield drop = an aid/timing/fit signal, not just noise |
| Melt | Post-deposit erosion | Melt spikes reward a melt-season touch |
| Net tuition revenue | The real target | Bigger class + higher discount can mean less revenue |

## Workflow

1. Pull the stage counts and compute each stage rate — attach the institution's definition for each (`[verify-at-use]`).
2. Compare each rate to prior year and to any benchmark (dated) — find the stage that moved.
3. Identify the cheapest lever to move that stage (top-funnel spend, admit-quality, aid, melt-season touch).
4. Model the net-revenue impact of the fix vs the alternative before recommending.

## Anti-patterns

- Spending on inquiries when the leak is at yield.
- Propping up the class with a rising admit rate.
- Reporting headcount without net tuition revenue.

## See also

- Traverse the **yield/melt intervention** tree in [`../../knowledge/higher-ed-decision-trees.md`](../../knowledge/higher-ed-decision-trees.md).
- [`../financial-aid-and-discount-rate/SKILL.md`](../financial-aid-and-discount-rate/SKILL.md), [`../../templates/enrollment-funnel-model.md`](../../templates/enrollment-funnel-model.md).
- Best practices: [`../../best-practices/model-the-funnel-not-the-headcount.md`](../../best-practices/model-the-funnel-not-the-headcount.md), [`../../best-practices/yield-is-cheaper-to-defend-than-to-replace.md`](../../best-practices/yield-is-cheaper-to-defend-than-to-replace.md).
