# The SaaS ARR Bridge Shows New, Expansion, Contraction, and Churn

**Status:** Absolute rule
**Domain:** FP&A / SaaS analytics
**Applies to:** `finance`

---

## Why this exists

Reporting ARR as a single closing balance obscures the most important signal in a SaaS business: the quality of growth. A company growing ARR 20% year-over-year can be doing so with 30% new bookings and 10% churn (a healthy engine) or with 50% new bookings and 30% churn (a leaky bucket spending its way to a treadmill). Collapsing the movements into a net change number makes both look identical. The ARR bridge — opening balance + new + expansion – contraction – churn = closing balance — is the minimum disclosure that tells a board or investor whether the growth engine is sound. It is also the input that drives NRR/GRR, LTV, and the Rule of 40, so a collapsed ARR figure propagates error forward to every metric derived from it.

## How to apply

Build the ARR bridge as a structured waterfall for every reporting period, and reconcile it to the closing balance before publishing any ARR-derived metric.

```
ARR Bridge Format (Monthly / Quarterly)
────────────────────────────────────────────────────
Opening ARR               $X,XXX,XXX
+ New ARR                 +$XXX,XXX    (first-time customers, period)
+ Expansion ARR           +$XXX,XXX    (upsell / cross-sell / seat growth, existing customers)
– Contraction ARR         –$XXX,XXX    (downgrades / seat reductions, existing customers)
– Churned ARR             –$XXX,XXX    (cancellations, non-renewals)
= Closing ARR             $X,XXX,XXX   ← must tie to the subscription ledger

Derived metrics:
  NRR = (Opening ARR + Expansion – Contraction – Churn) / Opening ARR
  GRR = (Opening ARR – Contraction – Churn) / Opening ARR
  Net new ARR = New + Expansion – Contraction – Churn
```

**Do:**
- Source each movement to the subscription management system or CRM — not to a manual tally.
- Define the ARR recognition policy (e.g., annualized MRR at period end, contract start date) and apply it consistently across all four movements.
- Report contraction separately from churn — a downgrade is a different operational problem than a cancellation and has a different fix.
- Reconcile the ARR bridge closing balance to the subscription ledger and to recognized deferred revenue.

**Don't:**
- Report "net new ARR" without splitting into its four components — a board cannot evaluate the go-to-market engine on a net number alone.
- Include professional services, one-time fees, or variable usage in ARR — ARR is recurring by definition; document what is excluded.
- Change the ARR definition between periods without restating prior periods and disclosing the change; definition drift destroys trend comparability.

## Edge cases / when the rule does NOT apply

- **Pre-revenue companies** with no ARR yet — the bridge applies as soon as the first contract is signed; build it from day one to establish the data discipline.
- **Usage-based businesses** where annual commitment is genuinely unknown — ARR is less meaningful; use Annual Recurring Revenue Run Rate (ARR-RR) with a clear definition, and flag that it is an estimate.

## See also

- [`../agents/fpa-analyst.md`](../agents/fpa-analyst.md) — owns SaaS analytics and the KPI-definition discipline.
- [`./fpa-kpi-definition-owns-every-deviation.md`](./fpa-kpi-definition-owns-every-deviation.md) — the ARR definition is a KPI definition; changes require the definition-change governance that rule specifies.

## Provenance

Codifies the fpa-analyst's SaaS growth analytics discipline from the finance plugin's knowledge file `knowledge/fpa-decision-support-and-unit-economics.md` (ARR bridge, NRR/GRR) and the `kpi-definition` skill's canonical SaaS definitions section. The four-movement bridge structure is standard SaaS investor and board reporting practice.

---

_Last reviewed: 2026-06-05 by `claude`_
