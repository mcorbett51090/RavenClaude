# Job Costing Closes the Loop Between Estimate and Actual

**Status:** Absolute rule
**Domain:** Job economics / P&L management
**Applies to:** `skilled-trades-contracting`

---

## Why this exists

An estimate without a job cost reconciliation is a guess that was never checked. Contractors who estimate but do not job-cost cannot know whether their pricing model is correct, cannot improve estimating accuracy over time, and cannot identify whether a job lost money due to a pricing error, a labor efficiency problem, or a material cost change. Job costing — comparing estimated labor hours, material cost, and subcontractor cost to actuals — is the feedback loop that improves every subsequent estimate. Contractors who job-cost consistently show lower estimating variance and higher job margins than those who rely on intuition alone.

## How to apply

Build the job cost reconciliation into every completed job above a minimum threshold:

```
Job cost reconciliation template (per job, post-completion):
  Job ID: ______   Customer: ______   Scope: ______

  LABOR:
    Estimated hours:          ______   Actual hours (time cards): ______
    Variance (hours):         ______   Variance (%): ______%
    Estimated labor cost ($): ______   Actual labor cost ($):     ______

  MATERIAL:
    Estimated material ($):   ______   Actual material ($):       ______
    Variance ($):             ______   Reason for variance (if >5%): ______

  SUBCONTRACTOR:
    Estimated sub cost ($):   ______   Actual sub cost ($):       ______

  TOTAL JOB COST:
    Estimated:                $______  Actual:                    $______
    Variance:                 $______  Variance (%):              ______%

  JOB MARGIN:
    Revenue:                  $______
    Actual total cost:        $______
    Gross job margin:         $______  (target: ≥ 30% for service; ≥ 20% for installation [unverified])

  Root cause flag (if variance > 10%):
    [ ] Estimating error (scope, hours, material)
    [ ] Field efficiency loss (rework, callbacks, difficult access)
    [ ] Material price change not captured in estimate
    [ ] Scope change not priced or approved
```

**Do:**
- Set a minimum job value threshold for formal job costing (e.g., every job > $1,500) — below that threshold, a simplified cost check is sufficient.
- Review job cost reports in the weekly operations meeting; a pattern of variance in labor hours is a training or scheduling signal.
- Feed job cost actuals back into the flat-rate book annually; the book should reflect the actual time it takes your techs, not the theoretical time.

**Don't:**
- Build a job cost system and then not act on the data — if variances are never discussed, the system becomes a reporting formality with no improvement value.
- Use job cost data to punish individual technicians for variance without first determining whether the variance is an estimating error vs. a field performance error.

## Edge cases / when the rule does NOT apply

T&M (time and materials) work where every hour and material item is billed to the customer has a different cost-recovery dynamic — job cost still applies to verify that the markup on materials and labor is being captured correctly, but the margin-protection function is different. Cost-plus contracts where the contractor passes costs through to the owner use job costing primarily to verify billing accuracy.

## See also

- [`../agents/trade-business-analyst.md`](../agents/trade-business-analyst.md) — owns the job cost system and the P&L variance analysis.
- [`../agents/estimating-specialist.md`](../agents/estimating-specialist.md) — uses job cost actuals to improve future estimates and flat-rate pricing.
- [`./first-time-fix-and-callback-rate-are-margin-not-just-quality.md`](./first-time-fix-and-callback-rate-are-margin-not-just-quality.md) — callbacks appear in job cost as negative-margin rework; the two rules connect directly.

## Provenance

Job costing methodology is fundamental in construction and trade contracting accounting; the practice is covered in construction accounting standards and contractor-specific financial management guides from CFMA (Construction Financial Management Association) and ACCA.

---

_Last reviewed: 2026-06-05 by `claude`_
