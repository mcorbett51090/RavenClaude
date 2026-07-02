# Auto-Repair Shop KPI Dashboard — <shop / period>

> Output template for a fixed-ops read across the three engines: shop economics, the front counter, and the bays. One per period. Every benchmark cell carries a source + date or `[verify-at-use]`; no customer PII.

## Header
- **Shop / location:** _____
- **Period:** _____  · **Prepared:** 2026-__-__
- **Baseline source:** _the shop's own prior period_

## 1. Shop economics (labor + parts)
| Metric | This period | Baseline | Benchmark (source + date) | Read |
|---|---|---|---|---|
| Effective labor rate (ELR) | | | _[verify-at-use]_ | |
| ELR-to-door-rate gap | | | n/a | |
| Labor gross profit % | | | _[verify-at-use]_ | |
| Parts gross profit % (blended) | | | _[ESTIMATE] [verify-at-use]_ | |
| Car count | | | n/a | |

## 2. Front counter (advisor / estimate)
| Metric | This period | Baseline | Benchmark (source + date) | Read |
|---|---|---|---|---|
| DVI completion rate | | | n/a | |
| Estimate close rate | | | _[verify-at-use]_ | |
| Hours per RO | | | _[ESTIMATE] [verify-at-use]_ | |
| Average RO / repair value | | | n/a | |
| Declined-work recovery | | | n/a | |

## 3. Bays (technician workflow)
| Metric | This period | Baseline | Benchmark (source + date) | Read |
|---|---|---|---|---|
| Productivity (clocked / available) | | | _[ESTIMATE] [verify-at-use]_ | |
| Efficiency (billed / clocked) | | | _[ESTIMATE] [verify-at-use]_ | |
| Proficiency (billed / actual) | | | _[ESTIMATE] [verify-at-use]_ | |
| Comeback rate | | | _[ESTIMATE] [verify-at-use]_ | |
| Average open-WIP age | | | n/a | |

## Headline + actions
- **Headline:** _the one number that moved and why_
- **Which profit engine is leaking:** _labor rate / productivity / parts margin / car count_
- **Top 2 actions:** _action — owner — expected GP or ELR movement — by when_
- **Two things that would change the answer:** _____

---
_Plus the ravenclaude-core Structured Output block. All rate / GP / productivity cells: verify-at-use against the shop's own numbers before acting._
