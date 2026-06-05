# Write-Off Discipline Separates Contractual Adjustments from Bad Debt

**Status:** Pattern
**Domain:** Revenue integrity / financial reporting
**Applies to:** `medical-revenue-cycle`

---

## Why this exists

Write-offs in a medical practice's A/R fall into fundamentally different categories with different causes and different owners. Contractual adjustments (the difference between billed charges and the payer's contracted allowable) are expected, pre-determined, and not a revenue loss — they are the correct reduction from a charge schedule that no one pays. Bad debt (patient balances deemed uncollectable) is a revenue loss. Incorrectly booking contractual adjustments as bad debt, or writing off bad debt without authorization, distorts both the net collection rate metric and the financial statements. A practice with 5% "bad debt" that is actually 80% misclassified contractual adjustments has a reporting problem that is masking the true bad-debt rate and the true collection performance.

## How to apply

Establish write-off categories, authorization levels, and a monthly reconciliation workflow.

```
Write-off category taxonomy:
CATEGORY 1 — Contractual adjustments (expected; no authorization required):
  - PPO/HMO/Medicare contractual write-off to contracted allowable
  - Medicaid write-off to Medicaid fee schedule
  - Self-pay adjustment per financial hardship policy
  → Automated in the billing system at time of remittance posting

CATEGORY 2 — Administrative write-offs (requires manager authorization):
  - Small balance write-offs below the practice's threshold (e.g., <$10)
  - Timely filing loss (see timely-filing rule)
  - Non-covered service patient responsibility where coverage was incorrectly represented
  → Requires: manager sign-off + root-cause documentation

CATEGORY 3 — Bad debt write-offs (requires director/CFO authorization):
  - Patient balances sent to collections and returned uncollected
  - Patient balance following financial hardship determination and charity-care grant
  - Balance > $500: legal review before write-off
  → Requires: director-level sign-off + hardship documentation or collections final report

Monthly write-off reconciliation:
  - Total write-offs by category vs. prior month vs. plan
  - Bad-debt write-off rate: bad debt ÷ net patient revenue × 100
    Target: ≤1% for a well-run practice [unverified — training knowledge; verify vs. MGMA]
  - Contractual adjustment rate: verify against the payer mix and contracted rates
  - Unauthorized write-offs: any write-off in Category 2 or 3 without required authorization → flag
```

**Do:**
- Configure the billing system to enforce the write-off category and authorization level at posting — manual override of the authorization workflow is an internal controls failure.
- Report bad-debt write-offs separately from contractual adjustments in the monthly P&L discussion — combining them hides the real collection performance.
- Review write-off authority levels annually; as the practice grows, the dollar thresholds should be reviewed and the level of authority confirmed.

**Don't:**
- Allow front-desk or billing staff to write off balances in Categories 2 or 3 without the required authorization — this is both a financial controls failure and a potential compliance risk.
- Use bad debt as a catch-all for any write-off that doesn't fit neatly elsewhere — misclassification inflates the apparent bad-debt rate and obscures the real issue.
- Ignore small-balance write-offs as trivial — if the practice writes off 1,000 claims per month at $8 average, that is $8k/month in a category that should have an SLA for prevention.

## Edge cases / when the rule does NOT apply

Federally Qualified Health Centers (FQHCs) and practices with sliding-fee scale programs have additional write-off categories driven by their program rules — the general taxonomy applies, but sliding-fee adjustments require their own category and documentation.

## See also

- [`../agents/rcm-analytics-analyst.md`](../agents/rcm-analytics-analyst.md) — owns the write-off analysis and reconciliation reporting.
- [`../agents/rcm-engagement-lead.md`](../agents/rcm-engagement-lead.md) — write-off discipline is a revenue integrity scope item in every RCM engagement.
- [`./net-collection-rate-not-gross-measures-the-cycle.md`](./net-collection-rate-not-gross-measures-the-cycle.md) — write-off categorization directly affects how net collection rate is calculated.

## Provenance

Standard RCM financial controls and revenue integrity practice; grounded in HFMA and MGMA write-off policy frameworks and healthcare financial management internal controls best practices.

---

_Last reviewed: 2026-06-05 by `claude`_
