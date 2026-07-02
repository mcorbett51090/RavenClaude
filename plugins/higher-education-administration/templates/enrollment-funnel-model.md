# Enrollment Funnel Model — <institution / entering term>

> Output template for modeling a class stage-by-stage and its net tuition revenue at each aid scenario. One per entering cohort. Every benchmark cell carries a source + date or `[verify-at-use]`; cohort-level only, no student PII.

## Header
- **Institution / program:** _____
- **Entering term / cohort:** _____  · **Prepared:** 2026-__-__
- **Baseline source:** _the institution's own prior cohort (IR)_
- **Definitions source:** _the institution's IR office (attach each stage definition)_

## 1. The funnel (stage rates)
| Stage | This cohort | Prior cohort | Definition (IR) | Read |
|---|---|---|---|---|
| Inquiries | | | _[verify-at-use]_ | |
| Apply rate (apps ÷ inquiries) | | | _[verify-at-use]_ | |
| Applications | | | _[verify-at-use]_ | |
| Admit rate (admits ÷ apps) | | | _[verify-at-use]_ | |
| Admits | | | _[verify-at-use]_ | |
| Yield (deposits ÷ admits) | | | _[verify-at-use]_ | |
| Deposits | | | _[verify-at-use]_ | |
| Melt ((dep − census) ÷ dep) | | | _[ESTIMATE] [verify-at-use]_ | |
| **Census enrollment** | | | _[verify-at-use]_ | |

> Class = inquiries × apply rate × admit rate × yield × (1 − melt). Name the stage that moved.

## 2. Net tuition revenue by aid scenario
| Scenario | Discount rate | Class size | Net tuition revenue | Break-even yield | Read |
|---|---|---|---|---|---|
| Current | | | | | |
| Discount +1 pt | | | | | _[verify-at-use]_ |
| Discount −1 pt | | | | | _[verify-at-use]_ |

> Net tuition revenue = gross tuition − institutional aid. A bigger class at a higher discount can mean less net revenue.

## 3. The leaking stage & the lever
- **Leaking stage:** _the one that moved vs prior cohort_
- **Cheapest lever to move it:** _top-funnel / admit-quality / aid-leverage / melt-season touch_
- **Aid segment with steepest yield response:** _____ `[verify-at-use]`

## Headline + actions
- **Headline:** _the one stage or number that decides the class and why_
- **Top 2 actions:** _action — owner — expected net-revenue movement — by when_
- **Two things that would change the answer:** _____

---
_Plus the ravenclaude-core Structured Output block. All benchmark/discount cells: verify-at-use against IR definitions before use._
