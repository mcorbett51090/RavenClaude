# Champion silence is a first-class churn signal, not an optional enrichment

**Status:** Pattern
**Domain:** CS analytics — signal design
**Applies to:** `customer-success-analytics`

---

## Why this exists

The departure or silence of a named product champion is one of the highest-precision churn predictors in B2B CS analytics. Accounts where the champion has left the company, changed roles, or stopped engaging with the CS team churn at a materially higher rate than accounts with active, named champions. Yet champion-presence data is often treated as an enrichment layer — nice to have but excluded from the tier rule because it requires a manual data-entry process or a CRM field that is inconsistently maintained. This rule makes champion signal a first-class tier input, not an optional add-on.

## How to apply

Design champion signal as a tier input from the start of the health mart build:

```
Champion-presence signals (in priority order):
  1. Named champion confirmed active in role THIS quarter (CRM field + last-activity date)
  2. Champion last engagement date (last email open / QBR attended / product login by champion)
  3. Champion-to-sponsor coverage (is there a backup if the primary champion leaves?)

Tier rule integration:
  Red trigger:  champion_last_contact_days > 60 AND renewal_proximity < 90
  Yellow flag:  champion_depth = 1 (single champion — single point of failure)
  Explainability: "Champion silent for N days" named as a tier driver
```

The CRM is the source of champion data; the `cs-analytics-architect` designs the champion-signal columns in `dim_account` and `fct_account_health_snapshot`. The `data-platform` pipeline lands the data from the CRM connector.

**Do:**
- Treat a single named champion as Yellow-flag worthy even when all usage signals are green — one-champion accounts are fragile by design.
- Name "Champion silent for N days" explicitly in the Red explainability panel — it is one of the clearest action drivers (the CS rep has a specific person to re-engage).
- Define "active" in a measurable way (not just "champion exists in CRM") — tie it to a last-contact or last-login event in the lookback window.

**Don't:**
- Mark champion data as "pending CRM cleanup" and defer it to phase 2 indefinitely — a tier without champion signal misses a major churn predictor.
- Use champion data from a name-only match (see `identity-resolution-is-upstream-never-reimplement-it.md`) — verify champion contact against a resolved account ID.

## Edge cases / when the rule does NOT apply

- Product-led growth (PLG) accounts with no named champion and no CS motion — champion signal is not applicable; route to a usage-only tier for PLG accounts.

## See also

- [`../skills/health-tier-design/SKILL.md`](../skills/health-tier-design/SKILL.md) — champion depth is a listed signal category in Step 2
- [`../agents/churn-signal-analyst.md`](../agents/churn-signal-analyst.md) — validates the predictive strength of champion signal in the back-test

## Provenance

Derived from standard B2B CS practice: champion departure is consistently among the top 3 churn predictors in SaaS renewal analysis. The specific measurable form (last-contact days, depth count) is the `cs-analytics-architect`'s operationalization of the general principle.

---

_Last reviewed: 2026-06-05 by `claude`_
