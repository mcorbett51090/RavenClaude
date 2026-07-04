# Craft-Beverage KPI Dashboard — <producer / period>

> Output template for an operations read across the three engines: production & cost, the tasting room & club (DTC), and distribution & compliance. One per period. Every benchmark cell carries a source + date or `[verify-at-use]`; three-tier / licensing / excise rows route to a professional; no PII.

## Header

- **Producer / location:** _____
- **Period:** _____ · **Prepared:** 2026-\_\_-\_\_
- **Baseline source:** _the producer's own prior period_

## 1. Production & cost

| Metric | This period | Baseline | Benchmark (source + date) | Read |
| --- | --- | --- | --- | --- |
| COGS per finished unit | | | _[ESTIMATE] [verify-at-use]_ | |
| Yield / loss rate | | | _[ESTIMATE] [verify-at-use]_ | |
| Packaging cost per unit | | | _[ESTIMATE] [verify-at-use]_ | |
| Vessel turns per year | | | _[ESTIMATE] [verify-at-use]_ | |

## 2. Channel margin & mix

| Metric | This period | Baseline | Benchmark (source + date) | Read |
| --- | --- | --- | --- | --- |
| DTC net margin per unit | | | _[ESTIMATE] [verify-at-use]_ | |
| Wholesale net margin per unit (after distributor + retailer) | | | _[ESTIMATE] [verify-at-use]_ | |
| Channel split (DTC % / wholesale %) | | | n/a | |
| Depletion rate (wholesale) | | | _[verify-at-use]_ | |

## 3. Tasting room & club (DTC)

| Metric | This period | Baseline | Benchmark (source + date) | Read |
| --- | --- | --- | --- | --- |
| Tasting-room purchase conversion | | | _[ESTIMATE] [verify-at-use]_ | |
| Club sign-up conversion | | | _[ESTIMATE] [verify-at-use]_ | |
| Club churn rate | | | _[ESTIMATE] [verify-at-use]_ | |
| Club member LTV | | | _[verify-at-use]_ | |

## 4. Distribution & compliance flags (route, do not decide)

| Item | Status | Flag | Routed to |
| --- | --- | --- | --- |
| Self-distribution eligibility | | _jurisdiction-specific [verify-at-use]_ | professional |
| Distributor franchise-law lock-in | | _jurisdiction-specific [verify-at-use]_ | professional |
| TTB / state licensing & permits | | _jurisdiction-specific [verify-at-use]_ | professional |
| Excise tax obligations | | _jurisdiction-specific [verify-at-use]_ | professional |

## Headline + actions

- **Headline:** _the one number that moved and why_
- **Top 2 actions:** _action — owner — expected metric movement — by when_
- **Two things that would change the answer:** _____

---

_Plus the ravenclaude-core Structured Output block. All benchmark cells: verify-at-use before an owner-facing number; three-tier / licensing / excise / tax / legal questions route to a licensed professional._
